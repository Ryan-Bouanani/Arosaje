<script setup>
import { ref } from 'vue';
import { useTheme } from 'vuetify';
import BackButton from '@/components/buttons/BackButton.vue';

const theme = useTheme();
const isDarkMode = ref(theme.global.name.value === 'dark');
const showAddPlantModal = ref(false);
const selectedPlante = ref(null);

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

const plantes = ref([
  { id: 1, nom: "Chrysanthème", photo: "/assets/persisted_img/chrysantheme.jpg", description: "Fleur d'automne résistante", dernierArrosage: "2024-02-10", prochainArrosage: "2024-02-17", sante: 85, temperatureIdeale: "15-20°C", exposition: "Soleil", engrais: "Tous les mois" },
  { id: 2, nom: "Jasmin", photo: "/assets/persisted_img/jasmin.jpg", description: "Plante grimpante parfumée", dernierArrosage: "2024-02-08", prochainArrosage: "2024-02-15", sante: 90, temperatureIdeale: "15-25°C", exposition: "Lumière indirecte", engrais: "Tous les mois" },
  { id: 3, nom: "Lavande", photo: "/assets/persisted_img/lavande.jpg", description: "Apprécie le soleil et un sol bien drainé", dernierArrosage: "2024-02-01", prochainArrosage: "2024-02-28", sante: 88, temperatureIdeale: "10-25°C", exposition: "Plein soleil", engrais: "Tous les 2 mois" },
  { id: 4, nom: "Lys", photo: "/assets/persisted_img/lys.jpg", description: "Fleur élégante au parfum intense", dernierArrosage: "2024-02-05", prochainArrosage: "2024-02-12", sante: 80, temperatureIdeale: "18-22°C", exposition: "Lumière indirecte", engrais: "Tous les 2 mois" },
  { id: 5, nom: "Marguerite", photo: "/assets/persisted_img/marguerite.jpg", description: "Fleur champêtre facile à cultiver", dernierArrosage: "2024-02-14", prochainArrosage: "2024-02-21", sante: 92, temperatureIdeale: "15-25°C", exposition: "Soleil", engrais: "Tous les mois" },
  { id: 6, nom: "Orchidée", photo: "/assets/persisted_img/orchidee.jpg", description: "Besoins spécifiques en humidité et lumière", dernierArrosage: "2024-02-08", prochainArrosage: "2024-02-15", sante: 85, temperatureIdeale: "16-24°C", exposition: "Lumière indirecte", engrais: "Tous les 15 jours" },
  { id: 7, nom: "Pivoine", photo: "/assets/persisted_img/pivoine.jpg", description: "Fleur spectaculaire au parfum envoûtant", dernierArrosage: "2024-02-12", prochainArrosage: "2024-02-18", sante: 90, temperatureIdeale: "15-20°C", exposition: "Soleil", engrais: "Tous les 2 mois" },
  { id: 8, nom: "Rose", photo: "/assets/persisted_img/rose.jpg", description: "Fleur emblématique au parfum délicat", dernierArrosage: "2024-02-07", prochainArrosage: "2024-02-14", sante: 85, temperatureIdeale: "15-25°C", exposition: "Soleil", engrais: "Tous les mois" },
  { id: 9, nom: "Tournesol", photo: "/assets/persisted_img/tournesol.jpg", description: "Fleur solaire qui suit la lumière", dernierArrosage: "2024-02-10", prochainArrosage: "2024-02-17", sante: 88, temperatureIdeale: "18-30°C", exposition: "Plein soleil", engrais: "Tous les mois" },
  { id: 10, nom: "Tulipe", photo: "/assets/persisted_img/tulipe.jpg", description: "Fleur printanière élégante", dernierArrosage: "2024-02-15", prochainArrosage: "2024-02-22", sante: 87, temperatureIdeale: "10-18°C", exposition: "Soleil", engrais: "Tous les 2 mois" }
]);


const addPlant = () => {
  if (newPlant.value.nom) {
    plantes.value.push({ ...newPlant.value, id: plantes.value.length + 1 });
    newPlant.value = { nom: '', photo: '', description: '', dernierArrosage: '', prochainArrosage: '', sante: 100, temperatureIdeale: '', exposition: '', engrais: '' };
    showAddPlantModal.value = false;
  }
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
          </v-card>
        </v-col>
      </v-row>
  
      <v-btn color="primary" class="d-flex align-center mt-6 mx-auto" @click="showAddPlantModal = true" elevation="10" rounded>
        <v-icon left>mdi-plus</v-icon>
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
        <v-col cols="6">
          <p class="text-body-1"><v-icon class="mr-2">mdi-flower-outline</v-icon><strong>Engrais :</strong></p>
          <p class="text-caption">{{ selectedPlante.engrais }}</p>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions class="justify-center">
      <v-btn color="primary" @click="selectedPlante = null">Fermer</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>

  
      <v-dialog v-model="showAddPlantModal" max-width="500px">
        <v-card>
          <v-card-title>Ajouter une plante</v-card-title>
          <v-card-text>
            <v-text-field label="Nom" v-model="newPlant.nom"></v-text-field>
            <v-text-field label="Photo (URL)" v-model="newPlant.photo"></v-text-field>
            <v-text-field label="Description" v-model="newPlant.description"></v-text-field>
            <v-text-field label="Dernier arrosage" v-model="newPlant.dernierArrosage" type="date"></v-text-field>
            <v-text-field label="Prochain arrosage" v-model="newPlant.prochainArrosage" type="date"></v-text-field>
            <v-slider label="Santé" v-model="newPlant.sante" min="0" max="100"></v-slider>
            <v-text-field label="Température idéale" v-model="newPlant.temperatureIdeale"></v-text-field>
            <v-text-field label="Exposition" v-model="newPlant.exposition"></v-text-field>
            <v-text-field label="Engrais" v-model="newPlant.engrais"></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn color="grey" @click="showAddPlantModal = false">Annuler</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="addPlant">Ajouter</v-btn>
          </v-card-actions>
        </v-card>
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