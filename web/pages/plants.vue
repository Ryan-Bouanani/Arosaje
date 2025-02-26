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


onMounted(() => {
  fetchPlants();
});

const openGuardPlantModal = (plant) => {
  if (plant) {
    selectedPlante.value = plant;
    showGuardPlantModal.value = true;
  }
};

const closePlantDialog = () => {
  selectedPlante.value = null;
};

</script>

<template>
  <v-container>
    <BackButton class="mr-4" />

    <v-row class="mb-4 align-center">
      <v-col cols="12" class="d-flex justify-space-between align-center">
        <v-card class="pa-4 text-center flex-grow-1" elevation="4">
          <v-card-title class="text-h4 font-weight-bold">Inventaire de plantes</v-card-title>
        </v-card>
        <v-btn color="green" class="ml-4" @click="showAddPlantModal = true">
          <v-icon class="mr-2">mdi-plus</v-icon>
          Ajouter une plante
        </v-btn>
      </v-col>
    </v-row>

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

    <v-dialog v-model="selectedPlante" max-width="500px">
  <v-card v-if="selectedPlante" class="pa-4">
    <v-card-title class="text-h5 text-center d-flex justify-space-between align-center">
      {{ selectedPlante.nom }}
      <v-btn icon @click="closePlantDialog">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>
    <v-img :src="selectedPlante.photo" height="200px" cover class="my-2 rounded-lg"></v-img>
    <v-divider></v-divider>
    <v-card-text>
      <v-row>
        <v-col cols="12">
          <p class="text-body-1">
            <v-icon class="mr-2">mdi-information-outline</v-icon>
            <strong>Description :</strong> {{ selectedPlante.description }}
          </p>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions class="justify-center">
      <v-btn color="primary" @click="openGuardPlantModal(selectedPlante)">
        Faire garder ma plante
      </v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>

    <v-dialog v-model="showGuardPlantModal" max-width="500px" persistent overlay-opacity="0.5">
      <GardePlant v-if="showGuardPlantModal"
        :plantName="selectedPlante?.nom || ''" 
        :plantPhoto="selectedPlante?.photo || ''"
        @close="showGuardPlantModal = false" />
    </v-dialog>

    <v-dialog v-model="showAddPlantModal" max-width="600px" persistent overlay-opacity="0.5">
      <PlantCard @close="showAddPlantModal = false" />
    </v-dialog>
  </v-container>
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