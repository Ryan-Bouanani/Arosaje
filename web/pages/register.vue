<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ApiService } from '~/services/api';

const router = useRouter();
const username = ref('');
const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const goToLogin = () => {
  router.push('/login');
};

const submitRegister = async () => {
  try {
    loading.value = true;
    error.value = '';

    const response = await ApiService.register({
      username: username.value,
      email: email.value,
      password: password.value
    });

    if (response.success) {
      // Rediriger vers la page de connexion après inscription réussie
      router.push('/login');
    } else {
      error.value = response.error || 'Une erreur est survenue';
    }
  } catch (e) {
    error.value = 'Une erreur est survenue lors de l\'inscription';
  } finally {
    loading.value = false;
  }
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
              <v-text-field
                v-model="username"
                label="Nom d'utilisateur"
                required
                :disabled="loading"
              ></v-text-field>
              
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                required
                :disabled="loading"
              ></v-text-field>
              
              <v-text-field
                v-model="password"
                label="Mot de passe"
                type="password"
                required
                :disabled="loading"
              ></v-text-field>

              <v-alert
                v-if="error"
                type="error"
                class="mb-4"
              >
                {{ error }}
              </v-alert>

              <v-btn
                @click="submitRegister"
                color="primary"
                class="mb-4"
                block
                :loading="loading"
                :disabled="loading"
                height="50"
              >
                S'inscrire
              </v-btn>

              <v-btn
                @click="goToLogin"
                color="success"
                block
                :disabled="loading"
                height="50"
              >
                Se connecter
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.v-btn {
  text-transform: none;
  font-size: 1.1rem;
}
</style>
