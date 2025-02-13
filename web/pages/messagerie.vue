<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import BackButton from '@/components/buttons/BackButton.vue';

const router = useRouter();

const messages = ref([
  { id: 1, auteur: "Alice", texte: "Je peux garder votre ficus cette semaine." },
  { id: 2, auteur: "Bob", texte: "Super, merci Alice !" }
]);

const nouveauMessage = ref("");

const envoyerMessage = () => {
  if (nouveauMessage.value) {
    messages.value.push({ id: messages.value.length + 1, auteur: "Moi", texte: nouveauMessage.value });
    nouveauMessage.value = "";
  }
};

const goTo = (page) => {
  router.push(`/${page}`);
};
</script>

<template>
  <v-container>

    <!-- Bouton Retour au Dashboard -->
    <BackButton class="mb-4" />

    <!-- Messagerie -->
    <v-card>
      <v-card-title>Messagerie</v-card-title>
      <v-list>
        <v-list-item v-for="msg in messages" :key="msg.id">
          <v-list-item-content>
            <v-list-item-title>{{ msg.auteur }} :</v-list-item-title>
            <v-list-item-subtitle>{{ msg.texte }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-text-field v-model="nouveauMessage" label="Écrire un message" />
      <v-btn @click="envoyerMessage">Envoyer</v-btn>
    </v-card>
  </v-container>
</template>
