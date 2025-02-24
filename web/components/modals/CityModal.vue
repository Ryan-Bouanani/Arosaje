<template>
    <v-dialog v-model="modelValue" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Modifier la ville</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newCity" label="Nouvelle Ville" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="$emit('update:modelValue', false)">Annuler</v-btn>
          <v-btn color="primary" @click="confirmCityChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const newCity = ref('');
  const confirmCityChange = () => {
    console.log('Ville modifiée en:', newCity.value);
    // Logique pour changer la ville
    $emit('update:modelValue', false);
  };
  </script>
  