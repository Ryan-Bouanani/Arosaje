<template>
    <v-dialog v-model="modelValue" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Modifier le numéro de téléphone</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newPhone" label="Nouveau numéro" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="$emit('update:modelValue', false)">Annuler</v-btn>
          <v-btn color="primary" @click="confirmPhoneChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const newPhone = ref('');
  const confirmPhoneChange = () => {
    console.log('Numéro de téléphone modifié en:', newPhone.value);
    // Logique pour changer le numéro
    $emit('update:modelValue', false);
  };
  </script>
  