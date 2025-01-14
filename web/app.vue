<script setup>
import { ref } from "vue";

// Gestion du thème
const darkTheme = ref(false);
const toggleTheme = () => {
  darkTheme.value = !darkTheme.value;
};
</script>

<template>
  <v-app :theme="darkTheme ? 'dark' : 'light'">
    <!-- Barre d'application -->
    <v-app-bar app color="light" dark>
      <v-img src="/assets/logo.svg" max-width="125" class="mr-4"></v-img>
      <v-spacer></v-spacer>
      <v-btn icon @click="toggleTheme">
        <v-icon>{{ darkTheme ? 'mdi-weather-sunny' : 'mdi-moon-waxing-crescent' }}</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- Contenu principal -->
    <v-main :style="darkTheme ? { backgroundColor: '#121212' } : { backgroundColor: '#ffffff' }">
      <NuxtPage />
    </v-main>

    <!-- Footer -->
    <v-footer app>
      <v-col class="text-center" cols="12">
        © 2025 A'rosa-je.
      </v-col>
    </v-footer>
  </v-app>
</template>

<style scoped>
.v-application {
  background-color: transparent;
}
</style>
