<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from 'vuetify';
import PlantCard from '~/components/PlantCard.vue';

const showAddPlantModal = ref(false);

const router = useRouter();
const theme = useTheme();

// État pour le drawer et le thème
const drawer = ref(true);
const isDarkMode = ref(false);

// Données enrichies pour les plantes
const plantes = ref([
  { 
    id: 1, 
    nom: "Chrysanthème", 
    photo: "/assets/persisted_img/chrysantheme.jpg", 
    description: "Fleur d'automne résistante",
    dernierArrosage: "2024-02-10",
    prochainArrosage: "2024-02-17",
    santé: 85,
    type: "Plante d'intérieur",
    besoins: "Un sol légèrement humide",
    soins: "Arrosage une fois par semaine, lumière indirecte"
  },
  { 
    id: 2, 
    nom: "Jasmin", 
    photo: "/assets/persisted_img/jasmin.jpg",
    description: "Plante grimpante parfumée",
    dernierArrosage: "2024-02-08",
    prochainArrosage: "2024-02-15",
    santé: 90,
    type: "Plante grimpante",
    besoins: "Sol bien drainé, humidité modérée",
    soins: "Arrosage modéré, lumière indirecte"
  },
  { 
    id: 3, 
    nom: "Lavande", 
    photo: "/assets/persisted_img/lavande.jpg", 
    description: "Apprécie le soleil et un sol bien drainé", 
    dernierArrosage: "2024-02-01", 
    prochainArrosage: "2024-02-28", 
    santé: 88, 
    type: "Plante aromatique",
    besoins: "Sol sec et bien drainé",
    soins: "Arrosage tous les 2 mois, exposition plein soleil"
  },
  { 
    id: 4, 
    nom: "Lys", 
    photo: "/assets/persisted_img/lys.jpg", 
    description: "Fleur élégante au parfum intense", 
    dernierArrosage: "2024-02-05", 
    prochainArrosage: "2024-02-12", 
    santé: 80, 
    type: "Plante à fleurs",
    besoins: "Sol bien drainé et léger",
    soins: "Arrosage modéré, lumière indirecte"
  },
  { 
    id: 5, 
    nom: "Marguerite", 
    photo: "/assets/persisted_img/marguerite.jpg", 
    description: "Fleur champêtre facile à cultiver", 
    dernierArrosage: "2024-02-14", 
    prochainArrosage: "2024-02-21", 
    santé: 92, 
    type: "Plante vivace",
    besoins: "Sol bien drainé, arrosage modéré",
    soins: "Arrosage tous les mois, plein soleil"
  },
  { 
    id: 6, 
    nom: "Orchidée", 
    photo: "/assets/persisted_img/orchidee.jpg", 
    description: "Besoins spécifiques en humidité et lumière", 
    dernierArrosage: "2024-02-08", 
    prochainArrosage: "2024-02-15", 
    santé: 85, 
    type: "Plante exotique",
    besoins: "Un substrat aéré, arrosage espacé",
    soins: "Tremper les racines une fois par semaine, lumière indirecte"
  },
  { 
    id: 7, 
    nom: "Pivoine", 
    photo: "/assets/persisted_img/pivoine.jpg", 
    description: "Fleur spectaculaire au parfum envoûtant", 
    dernierArrosage: "2024-02-12", 
    prochainArrosage: "2024-02-18", 
    santé: 90, 
    type: "Plante à fleurs",
    besoins: "Sol légèrement humide, lumière indirecte",
    soins: "Arrosage hebdomadaire, exposition au soleil"
  }
]);

// Statistiques
const stats = ref({
  totalPlantes: 3,
  plantesEnSanté: 2,
  plantesàArroser: 1
});

// Notifications
const notifications = ref([
  { 
    id: 1, 
    message: "Arrosage prévu pour le Ficus", 
    type: "warning",
    date: new Date()
  }
]);

// Plante sélectionnée pour la vue détaillée
const selectedPlante = ref(null);

// Méthodes
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  theme.global.name.value = isDarkMode.value ? 'dark' : 'light';
};

// Méthode de navigation
const goTo = (page) => {
  if (page === 'ajouter-plante') {
    router.push({ name: 'AddPlant' }); // Utilisation du name de la route
  } else {
    router.push(`/${page}`);
  }
};

// Méthode de déconnexion
const logout = () => {
  // Ici vous pouvez ajouter la logique de déconnexion (supprimer le token, etc.)
  router.push('/login');
};

const needsWater = (plante) => {
  return new Date(plante.prochainArrosage) <= new Date();
};

const arroserPlante = (plante) => {
  const index = plantes.value.findIndex(p => p.id === plante.id);
  if (index !== -1) {
    plantes.value[index].dernierArrosage = new Date().toLocaleDateString();
    
    // Calcul de la prochaine date d'arrosage
    const nextWateringDate = new Date();
    nextWateringDate.setDate(nextWateringDate.getDate() + 7); // +7 jours
    plantes.value[index].prochainArrosage = nextWateringDate.toLocaleDateString();
    
    // Augmentation de la santé de 20 %, mais max 100 %
    plantes.value[index].santé = Math.min(plantes.value[index].santé + 20, 100);

    // Ajouter une notification
    notifications.value.push({
      id: Date.now(),
      message: `Plante ${plante.nom} arrosée (+20% santé)`,
      type: 'info',
      date: new Date()
    });
  }
};

const voirDetails = (plante) => {
  selectedPlante.value = plante; // Ouvre la vue détaillée
};

onMounted(() => {
  // Animation de chargement des données
});
</script>

<template>
  <v-app :theme="isDarkMode ? 'dark' : 'light'">
    <!-- Navigation drawer avec effet de transition -->
    <v-navigation-drawer
      v-model="drawer"
      app
      class="rounded-tr-xl"
      elevation="4"
      :rail="!drawer"
    >
      <v-list-item
        title="Mon Dashboard"
        subtitle="Gestion des plantes"
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-chevron-left"
            @click.stop="drawer = !drawer"
          ></v-btn>
        </template>
      </v-list-item>

      <v-divider></v-divider>

      <!-- Menu avec animations au survol -->
      <v-list-item
  v-for="(item, index) in [
    { title: 'Plantes', icon: 'mdi-leaf', route: 'plants' },
    { title: 'Messagerie', icon: 'mdi-message', route: 'messagerie' },
    { title: 'Historique', icon: 'mdi-history', route: 'historique' },
    { title: 'Paramètres', icon: 'mdi-cog', route: 'parametre' }
  ]"
  :key="index"
  :value="item"
  :to="item.route"
  @click="item.route === 'messagerie' ? dialog.value = true : goTo(item.route)"
  class="menu-item"
>
  <template v-slot:prepend>
    <v-icon :icon="item.icon"></v-icon>
  </template>
  <v-list-item-title>{{ item.title }}</v-list-item-title>
</v-list-item>

      <template v-slot:append>
        <v-list density="compact" nav>
          <v-list-item @click="toggleTheme">
            <template v-slot:prepend>
              <v-icon :icon="isDarkMode ? 'mdi-weather-night' : 'mdi-weather-sunny'"></v-icon>
            </template>
            <v-list-item-title>{{ isDarkMode ? 'Mode clair' : 'Mode sombre' }}</v-list-item-title>
          </v-list-item>
          
          <v-list-item @click="logout" class="logout-item">
            <template v-slot:prepend>
              <v-icon color="error">mdi-logout</v-icon>
            </template>
            <v-list-item-title class="text-error">Déconnexion</v-list-item-title>
          </v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <!-- Contenu principal avec carte de statistiques -->
    <v-main class="bg-grey-lighten-3">
      <v-container fluid>
        <!-- Résumé des statistiques -->
        <v-row class="mb-6">
          <v-col cols="12" md="4">
            <v-card elevation="2" class="rounded-lg">
              <v-card-item>
                <v-icon size="32" color="primary" class="mb-2">mdi-flower</v-icon>
                <div class="text-h6">{{ stats.totalPlantes }}</div>
                <div class="text-subtitle-2">Plantes totales</div>
              </v-card-item>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card elevation="2" class="rounded-lg">
              <v-card-item>
                <v-icon size="32" color="success" class="mb-2">mdi-heart-pulse</v-icon>
                <div class="text-h6">{{ stats.plantesEnSanté }}</div>
                <div class="text-subtitle-2">Plantes en bonne santé</div>
              </v-card-item>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card elevation="2" class="rounded-lg">
              <v-card-item>
                <v-icon size="32" color="warning" class="mb-2">mdi-water</v-icon>
                <div class="text-h6">{{ stats.plantesàArroser }}</div>
                <div class="text-subtitle-2">Plantes à arroser</div>
              </v-card-item>
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <!-- Liste des plantes avec animation -->
          <v-col cols="12" md="8">
            <v-card elevation="2" class="rounded-lg">
              <v-card-title class="d-flex justify-space-between align-center pa-4">
                <span class="text-h6">Mes plantes</span>
                <v-btn color="green" @click="showAddPlantModal = true">
                  <v-icon class="mr-2">mdi-plus</v-icon>
                  Ajouter une plante
                </v-btn>
              </v-card-title>

              <v-container fluid>
                <v-row>
                  <v-col v-for="plante in plantes" :key="plante.id" cols="12" sm="6" lg="4">
                    <v-card
                      elevation="4"
                      class="h-100 plant-card"
                      :class="{ 'needs-water': needsWater(plante) }"
                    >
                      <v-img
                        :src="plante.photo"
                        height="200"
                        cover
                        class="align-end"
                      >
                        <v-card-title class="text-white bg-black bg-opacity-50">
                          {{ plante.nom }}
                        </v-card-title>
                      </v-img>

                      <v-card-text>
                        <div class="d-flex align-center mb-2">
                          <v-icon color="primary" class="mr-2">mdi-water</v-icon>
                          <span>Prochain arrosage: {{ plante.prochainArrosage }}</span>
                        </div>
                        <v-progress-linear
                          :model-value="plante.santé"
                          color="success"
                          height="8"
                          rounded
                        ></v-progress-linear>
                      </v-card-text>

                      <v-card-actions class="d-flex justify-space-between">
                        <v-btn 
                          variant="elevated" 
                          color="primary"
                          prepend-icon="mdi-information"
                          @click="voirDetails(plante)"
                        >
                          Détails
                        </v-btn>

                        <v-btn 
                          variant="elevated" 
                          :color="needsWater(plante) ? 'error' : 'success'"
                          prepend-icon="mdi-water"
                          @click="arroserPlante(plante)"
                        >
                          Arroser
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
            </v-card>
          </v-col>

          <!-- Modal de détails de la plante -->
          <v-dialog v-model="selectedPlante" max-width="600px">
            <v-card>
              <v-card-title>
                <span class="text-h5">Détails de {{ selectedPlante?.nom }}</span>
              </v-card-title>

              <v-card-text>
                <v-img :src="selectedPlante?.photo" height="200" class="mb-4"></v-img>
                <div><strong>Description:</strong> {{ selectedPlante?.description }}</div>
                <div><strong>Type:</strong> {{ selectedPlante?.type }}</div>
                <div><strong>Besoins:</strong> {{ selectedPlante?.besoins }}</div>
                <div><strong>Soins:</strong> {{ selectedPlante?.soins }}</div>
                <div><strong>Dernier arrosage:</strong> {{ selectedPlante?.dernierArrosage }}</div>
                <div><strong>Prochain arrosage:</strong> {{ selectedPlante?.prochainArrosage }}</div>
              </v-card-text>

              <v-card-actions>
                <v-btn color="primary" @click="selectedPlante = null">Fermer</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-row>
      </v-container>
    </v-main>
    <v-dialog v-model="showAddPlantModal" max-width="600px" persistent overlay-opacity="0.5">
  <PlantCard @close="showAddPlantModal = false" />
</v-dialog>

  </v-app>
</template>
