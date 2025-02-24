<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ApiService } from '~/services/api';

const router = useRouter();
const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const goToRegister = () => {
  router.push('/register');
};

const submitLogin = async () => {
  try {
    loading.value = true;
    error.value = '';

    const response = await ApiService.login({
      email: email.value,
      password: password.value
    });

    if (response.success) {
      // Rediriger vers la page d'accueil après connexion réussie
      router.push('/dashboard');
    } else {
      error.value = response.error || 'Une erreur est survenue';
    }
  } catch (e) {
    error.value = 'Une erreur est survenue lors de la connexion';
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
          <v-card-title class="text-h5">Connexion</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submitLogin">
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
                @click="submitLogin"
                color="success"
                class="mb-4"
                block
                :loading="loading"
                :disabled="loading"
                height="50"
              >
                Se connecter
              </v-btn>
            </v-form>

            <v-btn
              @click="goToRegister"
              color="primary"
              block
              :disabled="loading"
              height="50"
            >
              S'inscrire
            </v-btn>
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
