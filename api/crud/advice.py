from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, not_, exists
from datetime import datetime

from models.advice import Advice, AdvicePriority, ValidationStatus
from models.plant_care import PlantCare, CareStatus
from models.plant import Plant
from models.user import User
from schemas.advice import AdviceCreate, AdviceUpdate, AdviceValidation, AdviceStats


class AdviceCRUD:

    def get_plant_cares_to_review(
        self,
        db: Session,
        botanist_id: int,
        priority_filter: Optional[AdvicePriority] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Récupère les gardes qui n'ont pas encore d'avis du botaniste connecté"""
        try:
            # Query pour les gardes sans avis du botaniste connecté
            query = (
                db.query(
                    PlantCare,
                    Plant.nom.label("plant_name"),
                    Plant.espece.label("plant_species"),
                    Plant.photo.label("plant_image_url"),
                    User.prenom.label("owner_prenom"),
                    User.nom.label("owner_nom"),
                    User.email.label("owner_email"),
                )
                .join(Plant, PlantCare.plant_id == Plant.id)
                .join(User, PlantCare.owner_id == User.id)
                .filter(
                    # Seulement les gardes actives
                    PlantCare.status.in_(
                        [
                            CareStatus.PENDING,
                            CareStatus.ACCEPTED,
                            CareStatus.IN_PROGRESS,
                        ]
                    ),
                    # Exclure les gardes qui ont déjà un avis de N'IMPORTE QUEL botaniste
                    not_(
                        exists().where(
                            and_(
                                Advice.plant_care_id == PlantCare.id,
                                Advice.is_current_version,
                            )
                        )
                    ),
                )
                .order_by(PlantCare.created_at.desc())
            )

            results = query.offset(skip).limit(limit).all()

            return [
                {
                    "id": result.PlantCare.id,
                    "plant_id": result.PlantCare.plant_id,
                    "start_date": (
                        result.PlantCare.start_date.isoformat()
                        if result.PlantCare.start_date
                        else None
                    ),
                    "end_date": (
                        result.PlantCare.end_date.isoformat()
                        if result.PlantCare.end_date
                        else None
                    ),
                    "care_instructions": result.PlantCare.care_instructions,
                    "localisation": result.PlantCare.localisation,
                    "plant_name": result.plant_name,
                    "plant_species": result.plant_species,
                    "plant_image_url": result.plant_image_url,
                    "owner_name": f"{result.owner_prenom} {result.owner_nom}",
                    "owner_email": result.owner_email,
                    "priority": AdvicePriority.NORMAL.value,  # Par défaut
                    "current_advice": None,
                    "advice_history": [],
                    "needs_validation": False,
                    "validation_count": 0,
                    "status": result.PlantCare.status.value,
                    "created_at": (
                        result.PlantCare.created_at.isoformat()
                        if result.PlantCare.created_at
                        else None
                    ),
                }
                for result in results
            ]

        except Exception as e:
            print(f"Erreur dans get_plant_cares_to_review: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_plant_cares_with_advice(
        self,
        db: Session,
        botanist_id: Optional[int] = None,
        validation_filter: Optional[ValidationStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Récupère les gardes qui ont déjà reçu un avis"""

        query = (
            db.query(
                PlantCare,
                Plant.nom.label("plant_name"),
                Plant.espece.label("plant_species"),
                Plant.photo.label("plant_image_url"),
                User.prenom.label("owner_prenom"),
                User.nom.label("owner_nom"),
                User.email.label("owner_email"),
            )
            .join(Plant, PlantCare.plant_id == Plant.id)
            .join(User, PlantCare.owner_id == User.id)
            .join(Advice, PlantCare.id == Advice.plant_care_id)
            .filter(Advice.is_current_version)
        )

        if botanist_id:
            query = query.filter(Advice.botanist_id == botanist_id)

        if validation_filter:
            query = query.filter(Advice.validation_status == validation_filter)

        # Tri par date de dernier conseil (plus récent en premier)
        query = query.order_by(desc(Advice.updated_at))

        results = query.offset(skip).limit(limit).all()

        # Pour chaque résultat, récupérer les détails du conseil actuel et l'historique
        plant_care_data = []
        for result in results:
            plant_care_id = result.PlantCare.id

            # Conseil actuel
            current_advice = (
                db.query(Advice)
                .options(joinedload(Advice.botanist), joinedload(Advice.validator))
                .filter(
                    and_(
                        Advice.plant_care_id == plant_care_id,
                        Advice.is_current_version,
                    )
                )
                .first()
            )

            # Historique des conseils
            advice_history = (
                db.query(Advice)
                .options(joinedload(Advice.botanist), joinedload(Advice.validator))
                .filter(Advice.plant_care_id == plant_care_id)
                .order_by(desc(Advice.created_at))
                .all()
            )

            # Compter les validations
            validation_count = len(
                [
                    a
                    for a in advice_history
                    if a.validation_status == ValidationStatus.VALIDATED
                ]
            )

            plant_care_data.append(
                {
                    "id": result.PlantCare.id,
                    "plant_id": result.PlantCare.plant_id,
                    "start_date": (
                        result.PlantCare.start_date.isoformat()
                        if result.PlantCare.start_date
                        else None
                    ),
                    "end_date": (
                        result.PlantCare.end_date.isoformat()
                        if result.PlantCare.end_date
                        else None
                    ),
                    "care_instructions": result.PlantCare.care_instructions,
                    "localisation": result.PlantCare.localisation,
                    "plant_name": result.plant_name,
                    "plant_species": result.plant_species,
                    "plant_image_url": result.plant_image_url,
                    "owner_name": f"{result.owner_prenom} {result.owner_nom}",
                    "owner_email": result.owner_email,
                    "priority": (
                        current_advice.priority.value
                        if current_advice and current_advice.priority
                        else "normal"
                    ),
                    "current_advice": (
                        current_advice.to_dict() if current_advice else None
                    ),
                    "advice_history": [advice.to_dict() for advice in advice_history],
                    "needs_validation": current_advice
                    and current_advice.validation_status == ValidationStatus.PENDING,
                    "validation_count": validation_count,
                }
            )

        return plant_care_data

    def create_advice(
        self, db: Session, advice_data: AdviceCreate, botanist_id: int
    ) -> Advice:
        """Créer un nouveau conseil botanique"""
        try:

            # Vérifier si c'est une mise à jour d'un conseil existant
            existing_advice = (
                db.query(Advice)
                .filter(
                    and_(
                        Advice.plant_care_id == advice_data.plant_care_id,
                        Advice.is_current_version,
                    )
                )
                .first()
            )

            if existing_advice:
                # Marquer l'ancien conseil comme non-current
                existing_advice.is_current_version = False

                # Créer la nouvelle version
                new_advice = Advice(
                    plant_care_id=advice_data.plant_care_id,
                    botanist_id=botanist_id,
                    title=advice_data.title,
                    content=advice_data.content,
                    priority=advice_data.priority,
                    version=existing_advice.version + 1,
                    previous_version_id=existing_advice.id,
                    is_current_version=True,
                )
            else:
                # Nouveau conseil
                new_advice = Advice(
                    plant_care_id=advice_data.plant_care_id,
                    botanist_id=botanist_id,
                    title=advice_data.title,
                    content=advice_data.content,
                    priority=advice_data.priority,
                    version=1,
                    is_current_version=True,
                )

            db.add(new_advice)
            db.commit()
            db.refresh(new_advice)

            return new_advice

        except Exception as e:
            print(f"Error in create_advice: {e}")
            import traceback

            traceback.print_exc()
            db.rollback()
            raise e

    def update_advice(
        self, db: Session, advice_id: int, advice_data: AdviceUpdate, botanist_id: int
    ) -> Optional[Advice]:
        """Mettre à jour un conseil existant (crée une nouvelle version)"""

        current_advice = (
            db.query(Advice)
            .filter(
                and_(
                    Advice.id == advice_id,
                    Advice.is_current_version,
                    Advice.botanist_id == botanist_id,
                )
            )
            .first()
        )

        if not current_advice:
            return None

        # Marquer l'ancien comme non-current
        current_advice.is_current_version = False

        # Créer la nouvelle version
        updated_fields = advice_data.dict(exclude_unset=True)

        new_advice = Advice(
            plant_care_id=current_advice.plant_care_id,
            botanist_id=botanist_id,
            title=updated_fields.get("title", current_advice.title),
            content=updated_fields.get("content", current_advice.content),
            priority=updated_fields.get("priority", current_advice.priority),
            version=current_advice.version + 1,
            previous_version_id=current_advice.id,
            is_current_version=True,
        )

        db.add(new_advice)
        db.commit()
        db.refresh(new_advice)

        return new_advice

    def validate_advice(
        self,
        db: Session,
        advice_id: int,
        validation_data: AdviceValidation,
        validator_id: int,
    ) -> Optional[Advice]:
        """Valider un conseil d'un autre botaniste"""

        advice = (
            db.query(Advice)
            .filter(
                and_(
                    Advice.id == advice_id,
                    Advice.is_current_version,
                    Advice.botanist_id
                    != validator_id,  # Ne peut pas valider ses propres conseils
                )
            )
            .first()
        )

        if not advice:
            return None

        advice.validation_status = validation_data.validation_status
        advice.validation_comment = validation_data.validation_comment
        advice.validator_id = validator_id
        advice.validated_at = datetime.utcnow()
        advice.botanist_notified = False  # Pour déclencher la notification

        db.commit()
        db.refresh(advice)

        return advice

    def get_advice_stats(
        self, db: Session, botanist_id: Optional[int] = None
    ) -> AdviceStats:
        """Obtenir les statistiques des conseils"""

        # Gardes à examiner (sans avis actuel)
        advised_plant_cares = (
            db.query(Advice.plant_care_id).filter(Advice.is_current_version).subquery()
        )

        to_review_count = (
            db.query(PlantCare)
            .filter(
                PlantCare.status.in_(
                    [CareStatus.PENDING, CareStatus.ACCEPTED, CareStatus.IN_PROGRESS]
                ),
                ~PlantCare.id.in_(advised_plant_cares),
            )
            .count()
        )

        # Gardes avec avis
        reviewed_count = db.query(Advice).filter(Advice.is_current_version).count()

        # Compteurs par priorité
        urgent_count = (
            db.query(Advice)
            .filter(
                and_(
                    Advice.is_current_version,
                    Advice.priority == AdvicePriority.URGENT,
                )
            )
            .count()
        )

        follow_up_count = (
            db.query(Advice)
            .filter(
                and_(
                    Advice.is_current_version,
                    Advice.priority == AdvicePriority.FOLLOW_UP,
                )
            )
            .count()
        )

        # En attente de validation
        pending_validation = (
            db.query(Advice)
            .filter(
                and_(
                    Advice.is_current_version,
                    Advice.validation_status == ValidationStatus.PENDING,
                )
            )
            .count()
        )

        # Conseils donnés par ce botaniste
        my_advice_count = 0
        my_validated_count = 0
        my_validations_done_count = 0

        if botanist_id:
            my_advice_count = (
                db.query(Advice)
                .filter(
                    and_(
                        Advice.botanist_id == botanist_id,
                        Advice.is_current_version,
                    )
                )
                .count()
            )

            # Mes conseils validés par d'autres botanistes
            my_validated_count = (
                db.query(Advice)
                .filter(
                    and_(
                        Advice.botanist_id == botanist_id,
                        Advice.is_current_version,
                        Advice.validation_status == ValidationStatus.VALIDATED,
                    )
                )
                .count()
            )

            # Validations que j'ai effectuées pour d'autres botanistes
            my_validations_done_count = (
                db.query(Advice).filter(Advice.validator_id == botanist_id).count()
            )

        return AdviceStats(
            total_to_review=to_review_count,
            total_reviewed=reviewed_count,
            urgent_count=urgent_count,
            follow_up_count=follow_up_count,
            pending_validation=pending_validation,
            my_advice_count=my_advice_count,
            my_validated_count=my_validated_count,
            my_validations_done_count=my_validations_done_count,
        )

    def get_advice_by_id(self, db: Session, advice_id: int) -> Optional[Advice]:
        """Récupérer un conseil par son ID"""
        return (
            db.query(Advice)
            .options(joinedload(Advice.botanist), joinedload(Advice.validator))
            .filter(Advice.id == advice_id)
            .first()
        )

    def get_plant_care_advice_history(
        self, db: Session, plant_care_id: int
    ) -> List[Advice]:
        """Récupérer l'historique complet des conseils pour une garde"""
        return (
            db.query(Advice)
            .options(joinedload(Advice.botanist), joinedload(Advice.validator))
            .filter(Advice.plant_care_id == plant_care_id)
            .order_by(desc(Advice.created_at))
            .all()
        )

    def get_current_plant_care_advice(
        self, db: Session, plant_care_id: int
    ) -> List[Advice]:
        """Récupérer seulement la dernière version des conseils pour une garde (par botaniste)"""
        # Sous-requête pour trouver la date de création la plus récente par botaniste
        subquery = (
            db.query(
                Advice.botanist_id, func.max(Advice.created_at).label("max_created_at")
            )
            .filter(Advice.plant_care_id == plant_care_id)
            .group_by(Advice.botanist_id)
            .subquery()
        )

        # Requête principale pour récupérer les conseils les plus récents
        return (
            db.query(Advice)
            .options(joinedload(Advice.botanist), joinedload(Advice.validator))
            .join(
                subquery,
                and_(
                    Advice.botanist_id == subquery.c.botanist_id,
                    Advice.created_at == subquery.c.max_created_at,
                ),
            )
            .filter(Advice.plant_care_id == plant_care_id)
            .order_by(desc(Advice.created_at))
            .all()
        )


# Instance globale
advice = AdviceCRUD()
