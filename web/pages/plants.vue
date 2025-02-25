<script setup>
import { ref } from 'vue';
import { useTheme } from 'vuetify';
import BackButton from '@/components/buttons/BackButton.vue';
import PlantCard from '~/components/PlantCard.vue';
import GardePlant from '~/components/GardePlant.vue';
import { ApiService } from '@/services/api';

const theme = useTheme();
const isDarkMode = ref(theme.global.name.value === 'dark');
const showAddPlantModal = ref(false);
const showGuardPlantModal = ref(false);
const selectedPlante = ref(null);

const plantes = ref([]);

const newPlant = ref({
  nom: '',
  photo: '',
  description: '',
  dernierArrosage: '',
  prochainArrosage: '',
  sante: 100,
  temperatureIdeale: '',
  exposition: '',
  engrais: ''
});

const fetchPlants = async () => {
  const response = await ApiService.getPlants();
  if (response.success) {
    console.log('response',response)
    plantes.value = response.data; // Récupère les plantes de l'API
  } else {
    console.error('Erreur de récupération des plantes:', response.error);
  }
};


onMounted(() => {
  fetchPlants();
});

const openGuardPlantModal = (plant) => {
  selectedPlante.value = plant;
  showGuardPlantModal.value = true;
};

</script>

<template>
    <v-container>
      <BackButton class="mr-4" />
      <v-row class="mb-4">
        <v-col cols="12">
          <v-card class="pa-4 text-center" elevation="4">
            <v-card-title class="text-h4 font-weight-bold">Inventaire de mes plantes</v-card-title>
          </v-card>
        </v-col>
      </v-row>
  
      <v-row>
        <v-col v-for="plant in plantes" :key="plant.id" cols="12" md="6" lg="4">
          <v-card class="plant-card" @click="selectedPlante = plant">
            <v-img :src="plant.photo" height="200px" cover></v-img>
            <v-card-title>{{ plant.nom }}</v-card-title>
            <v-card-subtitle><strong>Conseil botaniste :</strong> {{ plant.description }}</v-card-subtitle>
            <v-card-text>
              <p><strong>Dernier arrosage :</strong> {{ plant.dernierArrosage }}</p>
              <p><strong>Prochain arrosage :</strong> {{ plant.prochainArrosage }}</p>
              <p><strong>Santé :</strong> {{ plant.sante }}%</p>
            </v-card-text>
            <v-btn color="primary" @click="openGuardPlantModal(plant)">Faire garder ma plante</v-btn>
          </v-card>
        </v-col>
      </v-row>
  
      <v-btn color="green" @click="showAddPlantModal = true">
                  <v-icon class="mr-2">mdi-plus</v-icon>
                  Ajouter une plante
                </v-btn>
  
                <v-dialog v-model="selectedPlante" max-width="500px">
    <v-card v-if="selectedPlante" class="pa-4">
      <v-card-title class="text-h5 text-center">{{ selectedPlante.nom }}</v-card-title>

      <v-img :src="selectedPlante.photo" height="200px" cover class="my-2 rounded-lg"></v-img>

      <v-divider></v-divider>

      <v-card-text>
        <v-row>
          <v-col cols="12">
            <p class="text-body-1"><v-icon class="mr-2">mdi-information-outline</v-icon><strong>Description :</strong> {{ selectedPlante.description }}</p>
          </v-col>
          <v-divider></v-divider>

          <v-col cols="6">
            <p class="text-body-1"><v-icon class="mr-2">mdi-calendar-clock</v-icon><strong>Dernier arrosage :</strong></p>
            <p class="text-caption">{{ selectedPlante.dernierArrosage }}</p>
          </v-col>
          <v-col cols="6">
            <p class="text-body-1"><v-icon class="mr-2">mdi-calendar-check</v-icon><strong>Prochain arrosage :</strong></p>
            <p class="text-caption">{{ selectedPlante.prochainArrosage }}</p>
          </v-col>
          <v-divider></v-divider>

          <v-col cols="6">
            <p class="text-body-1"><v-icon class="mr-2">mdi-heart-pulse</v-icon><strong>Santé :</strong></p>
            <p class="text-caption">{{ selectedPlante.sante }}%</p>
          </v-col>
          <v-col cols="6">
            <p class="text-body-1"><v-icon class="mr-2">mdi-thermometer</v-icon><strong>Température idéale :</strong></p>
            <p class="text-caption">{{ selectedPlante.temperatureIdeale }}</p>
          </v-col>
          <v-divider></v-divider>

          <v-col cols="6">
            <p class="text-body-1"><v-icon class="mr-2">mdi-white-balance-sunny</v-icon><strong>Exposition :</strong></p>
            <p class="text-caption">{{ selectedPlante.exposition }}</p>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
<v-dialog v-model="showGuardPlantModal" max-width="500px" persistent overlay-opacity="0.5">
  <GardePlant :plantName="selectedPlante.nom" @close="showGuardPlantModal = false" />
</v-dialog>
    </v-container>
    <v-dialog v-model="showAddPlantModal" max-width="600px" persistent overlay-opacity="0.5">
  <PlantCard @close="showAddPlantModal = false" />
</v-dialog>
  </template>
  
  <style scoped>
  .plant-card {
    cursor: pointer;
    transition: 0.3s;
    border-radius: 12px;
    overflow: hidden;
  }
  
  .plant-card:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  }
  
  .v-btn {
    transition: all 0.3s ease;
  }
  
  .v-btn:hover {
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    transform: scale(1.05);
  }
  
  .v-dialog {
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
  </style>