<template>
    <v-dialog v-model="modelValue" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Modifier le nom complet</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newFirstName" label="Prénom" required></v-text-field>
          <v-text-field v-model="newLastName" label="Nom" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="$emit('update:modelValue', false)">Annuler</v-btn>
          <v-btn color="primary" @click="confirmFullNameChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const newFirstName = ref('');
  const newLastName = ref('');
  const confirmFullNameChange = () => {
    console.log('Nom complet modifié:', newFirstName.value, newLastName.value);
    // Logique pour changer le nom complet
    $emit('update:modelValue', false);
  };
  </script>
  