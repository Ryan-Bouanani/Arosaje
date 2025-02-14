<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from 'vuetify';

const router = useRouter();
const theme = useTheme();

// État pour le drawer et le thème
const drawer = ref(true);
const isDarkMode = ref(false);

// Données enrichies pour les plantes
const plantes = ref([
  { 
    id: 1, 
    nom: "Ficus", 
    photo: "/ficus.jpg", 
    description: "Besoin d'arrosage régulier",
    dernierArrosage: "2024-02-10",
    prochainArrosage: "2024-02-17",
    santé: 85
  },
  // ... autres plantes avec données similaires
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

// Méthodes
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  theme.global.name.value = isDarkMode.value ? 'dark' : 'light';
};

const goTo = (page) => {
  router.push(`/${page}`);
};

const logout = () => {
  router.push('/login');
};

const needsWater = (plante) => {
  return new Date(plante.prochainArrosage) <= new Date();
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
      <v-list density="compact" nav>
        <v-list-item
          v-for="(item, index) in [
            { title: 'Plantes', icon: 'mdi-leaf', route: 'plantes' },
            { title: 'Messagerie', icon: 'mdi-message', route: 'messagerie' },
            { title: 'Historique', icon: 'mdi-history', route: 'historique' },
            { title: 'Paramètres', icon: 'mdi-cog', route: 'parametre' }
          ]"
          :key="index"
          :value="item"
          :to="item.route"
          @click="goTo(item.route)"
          class="menu-item"
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon"></v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>

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
                <v-btn
                  color="primary"
                  prepend-icon="mdi-plus"
                  @click="goTo('')"
                  variant="elevated"
                >
                  Ajouter une plante
                </v-btn>
              </v-card-title>

              <v-container fluid>
                <v-row>
                  <v-col v-for="plante in plantes" :key="plante.id" cols="12" sm="6" lg="4">
                    <v-card
                      elevation="2"
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

                      <v-card-actions>
                        <v-btn variant="text" color="primary">
                          Détails
                        </v-btn>
                        <v-btn variant="text" color="primary">
                          Arroser
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-col>
                </v-row>
              </v-container>
            </v-card>
          </v-col>

          <!-- Panel latéral avec notifications -->
          <v-col cols="12" md="4">
            <v-card elevation="2" class="rounded-lg">
              <v-card-title class="pa-4">
                <span class="text-h6">Notifications</span>
              </v-card-title>

              <v-list>
                <v-list-item
                  v-for="notif in notifications"
                  :key="notif.id"
                  :subtitle="new Date(notif.date).toLocaleDateString()"
                >
                  <template v-slot:prepend>
                    <v-icon :color="notif.type === 'warning' ? 'warning' : 'info'">
                      {{ notif.type === 'warning' ? 'mdi-alert' : 'mdi-information' }}
                    </v-icon>
                  </template>
                  {{ notif.message }}
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.menu-item {
  transition: background-color 0.3s ease;
}

.menu-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.logout-item:hover {
  background-color: rgba(var(--v-theme-error), 0.1);
}

.plant-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.plant-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

.needs-water {
  border: 2px solid var(--v-theme-warning);
}
</style>