<template>
    <v-dialog v-model="modelValue" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Modifier l'email</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newEmail" label="Nouvel Email" type="email" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="$emit('update:modelValue', false)">Annuler</v-btn>
          <v-btn color="primary" @click="confirmEmailChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const newEmail = ref('');
  const confirmEmailChange = () => {
    console.log('Email modifié en:', newEmail.value);
    // Logique pour changer l'email
    $emit('update:modelValue', false);
  };
  </script>
  