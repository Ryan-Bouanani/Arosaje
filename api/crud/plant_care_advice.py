from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func, text, not_, exists
from datetime import datetime, timedelta

from models.plant_care_advice import PlantCareAdvice, AdvicePriority, ValidationStatus
from models.plant_care import PlantCare, CareStatus
from models.plant import Plant
from models.user import User, UserRole
from schemas.plant_care_advice import (
    PlantCareAdviceCreate, 
    PlantCareAdviceUpdate, 
    PlantCareAdviceValidation,
    PlantCareWithAdvice,
    AdviceStats
)

class PlantCareAdviceCRUD:
    
    def get_plant_cares_to_review(
        self, 
        db: Session, 
        botanist_id: int,
        priority_filter: Optional[AdvicePriority] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupère les gardes qui n'ont pas encore d'avis du botaniste connecté"""
        try:
            # Query pour les gardes sans avis du botaniste connecté
            query = db.query(
                PlantCare,
                Plant.nom.label('plant_name'),
                Plant.espece.label('plant_species'),
                Plant.photo.label('plant_image_url'),
                User.prenom.label('owner_prenom'),
                User.nom.label('owner_nom'),
                User.email.label('owner_email')
            ).join(
                Plant, PlantCare.plant_id == Plant.id
            ).join(
                User, PlantCare.owner_id == User.id
            ).filter(
                # Seulement les gardes actives
                PlantCare.status.in_([CareStatus.PENDING, CareStatus.ACCEPTED, CareStatus.IN_PROGRESS]),
                # Exclure les gardes qui ont déjà un avis de N'IMPORTE QUEL botaniste
                not_(exists().where(
                    and_(
                        PlantCareAdvice.plant_care_id == PlantCare.id,
                        PlantCareAdvice.is_current_version == True
                    )
                ))
            ).order_by(
                PlantCare.created_at.desc()
            )
            
            results = query.offset(skip).limit(limit).all()
            
            return [
                {
                    'id': result.PlantCare.id,
                    'plant_id': result.PlantCare.plant_id,
                    'start_date': result.PlantCare.start_date.isoformat() if result.PlantCare.start_date else None,
                    'end_date': result.PlantCare.end_date.isoformat() if result.PlantCare.end_date else None,
                    'care_instructions': result.PlantCare.care_instructions,
                    'localisation': result.PlantCare.localisation,
                    'plant_name': result.plant_name,
                    'plant_species': result.plant_species,
                    'plant_image_url': result.plant_image_url,
                    'owner_name': f"{result.owner_prenom} {result.owner_nom}",
                    'owner_email': result.owner_email,
                    'priority': AdvicePriority.NORMAL.value,  # Par défaut
                    'current_advice': None,
                    'advice_history': [],
                    'needs_validation': False,
                    'validation_count': 0,
                    'status': result.PlantCare.status.value,
                    'created_at': result.PlantCare.created_at.isoformat() if result.PlantCare.created_at else None
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
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupère les gardes qui ont déjà reçu un avis"""
        
        query = db.query(
            PlantCare,
            Plant.nom.label('plant_name'),
            Plant.espece.label('plant_species'),
            Plant.photo.label('plant_image_url'),
            User.prenom.label('owner_prenom'),
            User.nom.label('owner_nom'),
            User.email.label('owner_email')
        ).join(
            Plant, PlantCare.plant_id == Plant.id
        ).join(
            User, PlantCare.owner_id == User.id
        ).join(
            PlantCareAdvice, PlantCare.id == PlantCareAdvice.plant_care_id
        ).filter(
            PlantCareAdvice.is_current_version == True
        )
        
        if botanist_id:
            query = query.filter(PlantCareAdvice.botanist_id == botanist_id)
            
        if validation_filter:
            query = query.filter(PlantCareAdvice.validation_status == validation_filter)
        
        # Tri par date de dernier conseil (plus récent en premier)
        query = query.order_by(desc(PlantCareAdvice.updated_at))
        
        results = query.offset(skip).limit(limit).all()
        
        # Pour chaque résultat, récupérer les détails du conseil actuel et l'historique
        plant_care_data = []
        for result in results:
            plant_care_id = result.PlantCare.id
            
            # Conseil actuel
            current_advice = db.query(PlantCareAdvice).options(
                joinedload(PlantCareAdvice.botanist),
                joinedload(PlantCareAdvice.validator)
            ).filter(
                and_(
                    PlantCareAdvice.plant_care_id == plant_care_id,
                    PlantCareAdvice.is_current_version == True
                )
            ).first()
            
            # Historique des conseils
            advice_history = db.query(PlantCareAdvice).options(
                joinedload(PlantCareAdvice.botanist),
                joinedload(PlantCareAdvice.validator)
            ).filter(
                PlantCareAdvice.plant_care_id == plant_care_id
            ).order_by(desc(PlantCareAdvice.created_at)).all()
            
            # Compter les validations
            validation_count = len([a for a in advice_history if a.validation_status == ValidationStatus.VALIDATED])
            
            plant_care_data.append({
                'id': result.PlantCare.id,
                'plant_id': result.PlantCare.plant_id,
                'start_date': result.PlantCare.start_date.isoformat() if result.PlantCare.start_date else None,
                'end_date': result.PlantCare.end_date.isoformat() if result.PlantCare.end_date else None,
                'care_instructions': result.PlantCare.care_instructions,
                'localisation': result.PlantCare.localisation,
                'plant_name': result.plant_name,
                'plant_species': result.plant_species,
                'plant_image_url': result.plant_image_url,
                'owner_name': f"{result.owner_prenom} {result.owner_nom}",
                'owner_email': result.owner_email,
                'priority': current_advice.priority.value if current_advice and current_advice.priority else "normal",
                'current_advice': current_advice.to_dict() if current_advice else None,
                'advice_history': [advice.to_dict() for advice in advice_history],
                'needs_validation': current_advice and current_advice.validation_status == ValidationStatus.PENDING,
                'validation_count': validation_count
            })
        
        return plant_care_data
    
    def create_advice(
        self, 
        db: Session, 
        advice_data: PlantCareAdviceCreate, 
        botanist_id: int
    ) -> PlantCareAdvice:
        """Créer un nouveau conseil botanique"""
        try:
            
            # Vérifier si c'est une mise à jour d'un conseil existant
            existing_advice = db.query(PlantCareAdvice).filter(
                and_(
                    PlantCareAdvice.plant_care_id == advice_data.plant_care_id,
                    PlantCareAdvice.is_current_version == True
                )
            ).first()
            
            if existing_advice:
                # Marquer l'ancien conseil comme non-current
                existing_advice.is_current_version = False
                
                # Créer la nouvelle version
                new_advice = PlantCareAdvice(
                    plant_care_id=advice_data.plant_care_id,
                    botanist_id=botanist_id,
                    title=advice_data.title,
                    content=advice_data.content,
                    priority=advice_data.priority,
                    version=existing_advice.version + 1,
                    previous_version_id=existing_advice.id,
                    is_current_version=True
                )
            else:
                # Nouveau conseil
                new_advice = PlantCareAdvice(
                    plant_care_id=advice_data.plant_care_id,
                    botanist_id=botanist_id,
                    title=advice_data.title,
                    content=advice_data.content,
                    priority=advice_data.priority,
                    version=1,
                    is_current_version=True
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
        self, 
        db: Session, 
        advice_id: int, 
        advice_data: PlantCareAdviceUpdate,
        botanist_id: int
    ) -> Optional[PlantCareAdvice]:
        """Mettre à jour un conseil existant (crée une nouvelle version)"""
        
        current_advice = db.query(PlantCareAdvice).filter(
            and_(
                PlantCareAdvice.id == advice_id,
                PlantCareAdvice.is_current_version == True,
                PlantCareAdvice.botanist_id == botanist_id
            )
        ).first()
        
        if not current_advice:
            return None
        
        # Marquer l'ancien comme non-current
        current_advice.is_current_version = False
        
        # Créer la nouvelle version
        updated_fields = advice_data.dict(exclude_unset=True)
        
        new_advice = PlantCareAdvice(
            plant_care_id=current_advice.plant_care_id,
            botanist_id=botanist_id,
            title=updated_fields.get('title', current_advice.title),
            content=updated_fields.get('content', current_advice.content),
            priority=updated_fields.get('priority', current_advice.priority),
            version=current_advice.version + 1,
            previous_version_id=current_advice.id,
            is_current_version=True
        )
        
        db.add(new_advice)
        db.commit()
        db.refresh(new_advice)
        
        return new_advice
    
    def validate_advice(
        self, 
        db: Session, 
        advice_id: int, 
        validation_data: PlantCareAdviceValidation,
        validator_id: int
    ) -> Optional[PlantCareAdvice]:
        """Valider un conseil d'un autre botaniste"""
        
        advice = db.query(PlantCareAdvice).filter(
            and_(
                PlantCareAdvice.id == advice_id,
                PlantCareAdvice.is_current_version == True,
                PlantCareAdvice.botanist_id != validator_id  # Ne peut pas valider ses propres conseils
            )
        ).first()
        
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
    
    def get_advice_stats(self, db: Session, botanist_id: Optional[int] = None) -> AdviceStats:
        """Obtenir les statistiques des conseils"""
        
        # Gardes à examiner (sans avis actuel)
        advised_plant_cares = db.query(PlantCareAdvice.plant_care_id).filter(
            PlantCareAdvice.is_current_version == True
        ).subquery()
        
        to_review_count = db.query(PlantCare).filter(
            PlantCare.status.in_([CareStatus.PENDING, CareStatus.ACCEPTED, CareStatus.IN_PROGRESS]),
            ~PlantCare.id.in_(advised_plant_cares)
        ).count()
        
        # Gardes avec avis
        reviewed_count = db.query(PlantCareAdvice).filter(
            PlantCareAdvice.is_current_version == True
        ).count()
        
        # Compteurs par priorité
        urgent_count = db.query(PlantCareAdvice).filter(
            and_(
                PlantCareAdvice.is_current_version == True,
                PlantCareAdvice.priority == AdvicePriority.URGENT
            )
        ).count()
        
        follow_up_count = db.query(PlantCareAdvice).filter(
            and_(
                PlantCareAdvice.is_current_version == True,
                PlantCareAdvice.priority == AdvicePriority.FOLLOW_UP
            )
        ).count()
        
        # En attente de validation
        pending_validation = db.query(PlantCareAdvice).filter(
            and_(
                PlantCareAdvice.is_current_version == True,
                PlantCareAdvice.validation_status == ValidationStatus.PENDING
            )
        ).count()
        
        # Conseils donnés par ce botaniste
        my_advice_count = 0
        my_validated_count = 0
        my_validations_done_count = 0
        
        if botanist_id:
            my_advice_count = db.query(PlantCareAdvice).filter(
                and_(
                    PlantCareAdvice.botanist_id == botanist_id,
                    PlantCareAdvice.is_current_version == True
                )
            ).count()
            
            # Mes conseils validés par d'autres botanistes
            my_validated_count = db.query(PlantCareAdvice).filter(
                and_(
                    PlantCareAdvice.botanist_id == botanist_id,
                    PlantCareAdvice.is_current_version == True,
                    PlantCareAdvice.validation_status == ValidationStatus.VALIDATED
                )
            ).count()
            
            # Validations que j'ai effectuées pour d'autres botanistes
            my_validations_done_count = db.query(PlantCareAdvice).filter(
                PlantCareAdvice.validator_id == botanist_id
            ).count()
        
        return AdviceStats(
            total_to_review=to_review_count,
            total_reviewed=reviewed_count,
            urgent_count=urgent_count,
            follow_up_count=follow_up_count,
            pending_validation=pending_validation,
            my_advice_count=my_advice_count,
            my_validated_count=my_validated_count,
            my_validations_done_count=my_validations_done_count
        )
    
    def get_advice_by_id(self, db: Session, advice_id: int) -> Optional[PlantCareAdvice]:
        """Récupérer un conseil par son ID"""
        return db.query(PlantCareAdvice).options(
            joinedload(PlantCareAdvice.botanist),
            joinedload(PlantCareAdvice.validator)
        ).filter(PlantCareAdvice.id == advice_id).first()
    
    def get_plant_care_advice_history(self, db: Session, plant_care_id: int) -> List[PlantCareAdvice]:
        """Récupérer l'historique complet des conseils pour une garde"""
        return db.query(PlantCareAdvice).options(
            joinedload(PlantCareAdvice.botanist),
            joinedload(PlantCareAdvice.validator)
        ).filter(
            PlantCareAdvice.plant_care_id == plant_care_id
        ).order_by(desc(PlantCareAdvice.created_at)).all()

    def get_current_plant_care_advice(self, db: Session, plant_care_id: int) -> List[PlantCareAdvice]:
        """Récupérer seulement la dernière version des conseils pour une garde (par botaniste)"""
        # Sous-requête pour trouver la date de création la plus récente par botaniste
        subquery = db.query(
            PlantCareAdvice.botanist_id,
            func.max(PlantCareAdvice.created_at).label('max_created_at')
        ).filter(
            PlantCareAdvice.plant_care_id == plant_care_id
        ).group_by(PlantCareAdvice.botanist_id).subquery()

        # Requête principale pour récupérer les conseils les plus récents
        return db.query(PlantCareAdvice).options(
            joinedload(PlantCareAdvice.botanist),
            joinedload(PlantCareAdvice.validator)
        ).join(
            subquery,
            and_(
                PlantCareAdvice.botanist_id == subquery.c.botanist_id,
                PlantCareAdvice.created_at == subquery.c.max_created_at
            )
        ).filter(
            PlantCareAdvice.plant_care_id == plant_care_id
        ).order_by(desc(PlantCareAdvice.created_at)).all()

# Instance globale
plant_care_advice = PlantCareAdviceCRUD()