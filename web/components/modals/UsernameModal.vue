<template>
    <v-dialog v-model="modelValue" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Modifier le nom d'utilisateur</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newUsername" label="Nouveau nom d'utilisateur" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="$emit('update:modelValue', false)">Annuler</v-btn>
          <v-btn color="primary" @click="confirmUsernameChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const newUsername = ref('');
  const confirmUsernameChange = () => {
    console.log('Nom d\'utilisateur modifié en:', newUsername.value);
    // Logique pour changer le nom d'utilisateur
    $emit('update:modelValue', false);
  };
  </script>
  