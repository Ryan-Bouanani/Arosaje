<script setup>
  import { useRouter } from 'vue-router';
  
  const router = useRouter();
  const goBack = () => {
    router.push('/dashboard');
  };
  </script>


<template>
    <v-btn color="secondary" @click="goBack">
      <v-icon left>mdi-arrow-left</v-icon>
      Retour au Dashboard
    </v-btn>
  </template>
  