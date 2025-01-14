<template>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="6" lg="4">
          <v-card>
            <v-card-title class="text-h5">Bienvenue sur A'rosa-je</v-card-title>
            <v-card-text>
              <v-btn @click="goToLogin" color="success" block>Se connecter</v-btn>
              <v-spacer></v-spacer>
              <v-btn @click="goToRegister" color="secondary" block>S'inscrire</v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
  const goToLogin = () => {
    
    useRouter().push('/login');
  };
  
  const goToRegister = () => {
    // Redirige l'utilisateur vers la page d'inscription
    useRouter().push('/register');
  };
  </script>
  