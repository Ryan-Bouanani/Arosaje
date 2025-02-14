<template>
    <v-dialog v-model="modelValue" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Changer le mot de passe</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="currentPassword" label="Mot de passe actuel" type="password" required></v-text-field>
          <v-text-field v-model="newPassword" label="Nouveau mot de passe" type="password" required></v-text-field>
          <v-text-field v-model="confirmPassword" label="Confirmer le mot de passe" type="password" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="$emit('update:modelValue', false)">Annuler</v-btn>
          <v-btn color="primary" @click="confirmPasswordChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const currentPassword = ref('');
  const newPassword = ref('');
  const confirmPassword = ref('');
  
  const confirmPasswordChange = () => {
    if (newPassword.value !== confirmPassword.value) {
      console.error("Les mots de passe ne correspondent pas.");
      return;
    }
    console.log('Mot de passe changé avec succès');
    // Logique pour changer le mot de passe
    $emit('update:modelValue', false);
  };
  </script>
  