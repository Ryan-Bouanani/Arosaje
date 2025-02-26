<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from 'vuetify';
import PlantCard from '~/components/PlantCard.vue';
import { ApiService } from '@/services/api';

const showAddPlantModal = ref(false);

const router = useRouter();
const theme = useTheme();
const plantes = ref([]);


// État pour le drawer et le thème
const drawer = ref(true);
const isDarkMode = ref(false);

// Données enrichies pour les plantes
const fetchPlants = async () => {
  const response = await ApiService.getPlants();
  if (response.success && Array.isArray(response.data)) {
    plantes.value = response.data.map(plant => ({
      ...plant,
      photo: ApiService.buildPhotoUrl(plant.photo) // Ajout de l'URL complète de l'image
    }));
  } else {
    console.error('Erreur de récupération des plantes:', response.error);
  }
};
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


onMounted(() => {
  fetchPlants();
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
                <v-tooltip text="Voir mes plantes" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn v-bind="props" icon="mdi-chevron-right" color="green" variant="tonal" @click="goTo('plants')"></v-btn>
                  </template>
                </v-tooltip>
              </v-card-title>

              <v-container fluid>
                <v-row>
                  <v-col v-for="plant in plantes" :key="plant.id" cols="12" md="6" lg="4">
                   <v-card class="plant-card" @click="selectedPlante = plant">
                     <v-img :src="plant.photo" height="200px" cover></v-img>
                     <v-card-title>{{ plant.nom }}</v-card-title>
                     <v-card-text class="text-body-2" style="max-height: 100px; overflow-y: auto;">
                      {{ plant.description }}
                    </v-card-text>
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
