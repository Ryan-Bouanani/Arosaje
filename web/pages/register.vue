<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ApiService } from '~/services/api';

const router = useRouter();
const nom = ref('');
const prenom = ref('');
const email = ref('');
const password = ref('');
const telephone = ref('');
const localisation = ref('');
const error = ref('');
const loading = ref(false);

const goToLogin = () => {
  router.push('/login');
};

const submitRegister = async () => {
  try {
    loading.value = true;
    error.value = '';

    // Vérification des champs obligatoires
    if (!nom.value || !prenom.value || !email.value || !password.value) {
      error.value = 'Veuillez remplir tous les champs obligatoires';
      return;
    }

    const response = await ApiService.register({
      nom: nom.value,
      prenom: prenom.value,
      email: email.value,
      password: password.value,
      telephone: telephone.value || undefined,
      localisation: localisation.value || undefined
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
                v-model="nom"
                label="Nom*"
                required
                :rules="[v => !!v || 'Le nom est obligatoire']"
                :disabled="loading"
              ></v-text-field>
              
              <v-text-field
                v-model="prenom"
                label="Prénom*"
                required
                :rules="[v => !!v || 'Le prénom est obligatoire']"
                :disabled="loading"
              ></v-text-field>
              
              <v-text-field
                v-model="email"
                label="Email*"
                type="email"
                required
                :rules="[
                  v => !!v || 'L\'email est obligatoire',
                  v => /.+@.+\..+/.test(v) || 'L\'email doit être valide'
                ]"
                :disabled="loading"
              ></v-text-field>
              
              <v-text-field
                v-model="password"
                label="Mot de passe*"
                type="password"
                required
                :rules="[
                  v => !!v || 'Le mot de passe est obligatoire',
                  v => v.length >= 8 || 'Le mot de passe doit contenir au moins 8 caractères'
                ]"
                :disabled="loading"
              ></v-text-field>

              <v-text-field
                v-model="telephone"
                label="Téléphone (optionnel)"
                :disabled="loading"
              ></v-text-field>

              <v-text-field
                v-model="localisation"
                label="Localisation (optionnel)"
                :disabled="loading"
              ></v-text-field>

              <v-alert
                v-if="error"
                type="error"
                class="mb-4"
              >
                {{ error }}
              </v-alert>

              <div class="text-caption mb-4 text-grey">
                * Champs obligatoires
              </div>

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
