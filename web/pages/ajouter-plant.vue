<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import BackButton from '@/components/buttons/BackButton.vue';

// Référence pour les données de la plante
const espece = ref('');
const description = ref('');
const photo = ref(null);

// Référence pour l'état du formulaire
const valid = ref(false);

// Router pour naviguer après ajout
const router = useRouter();

// Fonction pour soumettre les données
const ajouterPlante = () => {
  // Vous pouvez ajouter votre logique pour envoyer les données au backend ici
  // envoyer la requête API pour ajouter la plante

  // Redirection après ajout
  router.push('/plantes');
};

// Fonction pour revenir au Dashboard
const retournerDashboard = () => {
  router.push('/dashboard'); // Remplacez "/" par la route de votre dashboard si nécessaire
};
</script>

<template>
  <v-container>
    <!-- Bouton retour Dashboard -->
    <BackButton class="mb-4" />

    <!-- Titre de la page -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">Ajouter une Plante</v-card-title>
          <v-card-subtitle>Saisissez les informations de la plante</v-card-subtitle>

          <!-- Formulaire d'ajout de plante -->
          <v-form v-model="valid">
            <!-- Espèce -->
            <v-text-field
              v-model="espece"
              label="Espèce"
              placeholder="Entrez l'espèce de la plante"
              required
            ></v-text-field>

            <!-- Description -->
            <v-textarea
              v-model="description"
              label="Description"
              placeholder="Entrez une description de la plante"
              rows="4"
            ></v-textarea>

            <!-- Photo -->
            <v-file-input
              v-model="photo"
              label="Photo de la plante"
              accept="image/*"
              show-size
              outlined
            ></v-file-input>

            <!-- Bouton de soumission -->
            <v-btn
              :disabled="!valid"
              color="success"
              @click="ajouterPlante"
              class="mt-4"
            >
              Ajouter la plante
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
