<script setup>
import { ref } from 'vue';


const username = ref('');
const email = ref('');
const password = ref('');
const submitRegister = () => {
};
</script>

<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="6" lg="4">
        <v-card>
          <v-card-title class="text-h5">Inscription</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submitRegister">
              <v-text-field v-model="username" label="Nom d'utilisateur" required></v-text-field>
              <v-text-field v-model="email" label="Email" type="email" required></v-text-field>
              <v-text-field v-model="password" label="Mot de passe" type="password" required></v-text-field>

              
              <v-btn @click="submitRegister" class="image-button" block>
                <v-img src="/assets/register-button.svg" contain></v-img>
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.image-button {
  cursor: pointer;
  width: 100%;
  height: auto;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
