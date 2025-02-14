<!-- Historique.vue -->
<script setup>
import { ref } from 'vue';
import BackButton from '@/components/buttons/BackButton.vue';

const historique = ref([
  { 
    id: 1, 
    nom: "Ficus", 
    dateDebut: "2024-01-10", 
    dateFin: "2024-01-20",
    status: "terminé",
    gardienNom: "Alice Martin",
    notes: "Arrosage effectué selon les instructions",
    photo: "/ficus.jpg"
  },
  { 
    id: 2, 
    nom: "Cactus", 
    dateDebut: "2024-02-01", 
    dateFin: "2024-02-15",
    status: "en cours",
    gardienNom: "Thomas Dubois",
    notes: "Plante en excellente condition",
    photo: "/cactus.jpg"
  }
]);

const getStatusColor = (status) => {
  return status === 'terminé' ? 'success' : 'info';
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
};
</script>

<template>
  <v-container class="pa-4">
    <div class="d-flex align-center mb-6">
      <BackButton class="mr-4" />
      <h1 class="text-h4 font-weight-medium">Historique des plantes gardées</h1>
    </div>

    <v-timeline density="comfortable" align="start">
      <v-timeline-item
        v-for="plante in historique"
        :key="plante.id"
        :dot-color="getStatusColor(plante.status)"
        size="small"
      >
        <template v-slot:opposite>
          <div class="text-caption">
            {{ formatDate(plante.dateDebut) }}
          </div>
        </template>

        <v-card elevation="2" class="mb-4">
          <div class="d-flex flex-no-wrap">
            <v-avatar
              class="ma-3"
              size="125"
              rounded="0"
            >
              <v-img :src="plante.photo" cover></v-img>
            </v-avatar>
            
            <div class="flex-grow-1 pa-4">
              <div class="d-flex justify-space-between align-center">
                <h3 class="text-h6 mb-1">{{ plante.nom }}</h3>
                <v-chip
                  :color="getStatusColor(plante.status)"
                  size="small"
                  class="text-capitalize"
                >
                  {{ plante.status }}
                </v-chip>
              </div>

              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="mr-1">mdi-account</v-icon>
                <span class="text-caption">Gardien: {{ plante.gardienNom }}</span>
              </div>

              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="mr-1">mdi-calendar-range</v-icon>
                <span class="text-caption">
                  Du {{ formatDate(plante.dateDebut) }} au {{ formatDate(plante.dateFin) }}
                </span>
              </div>

              <v-expand-transition>
                <div>
                  <v-divider class="my-2"></v-divider>
                  <div class="text-caption">{{ plante.notes }}</div>
                </div>
              </v-expand-transition>
            </div>
          </div>
        </v-card>
      </v-timeline-item>
    </v-timeline>
  </v-container>
</template>