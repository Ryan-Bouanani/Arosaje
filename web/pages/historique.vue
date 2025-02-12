<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const historique = ref([
  { id: 1, nom: "Ficus", dateDebut: "2024-01-10", dateFin: "2024-01-20" },
  { id: 2, nom: "Cactus", dateDebut: "2024-02-01", dateFin: "2024-02-15" }
]);

const goTo = (page) => {
  router.push(`/${page}`);
};
</script>

<template>
  <v-container>
    <!-- Bouton Retour au Dashboard -->
    <v-btn color="green" @click="goTo('dashboard')" class="mb-4">
      <v-icon left>mdi-arrow-left</v-icon>
      Retour au Dashboard
    </v-btn>

    <!-- Historique des plantes gardées -->
    <v-card>
      <v-card-title>Historique des plantes gardées</v-card-title>
      <v-list>
        <v-list-item v-for="plante in historique" :key="plante.id">
          <v-list-item-content>
            <v-list-item-title>{{ plante.nom }}</v-list-item-title>
            <v-list-item-subtitle>Gardée du {{ plante.dateDebut }} au {{ plante.dateFin }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-container>
</template>
