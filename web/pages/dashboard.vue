<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const plantes = ref([
  { id: 1, nom: "Ficus", photo: "/ficus.jpg", description: "Besoin d’arrosage régulier" },
  { id: 2, nom: "Cactus", photo: "/cactus.jpg", description: "Arrosage rare" },
  { id: 3, nom: "Orchidée", photo: "/orchidee.jpg", description: "Arrosage 1 fois par semaine" }
]);

const goTo = (page) => {
  router.push(`/${page}`);
};

const logout = () => {
  router.push('/login');
};
</script>

<template>
  <v-app>
    <!-- Barre de navigation latérale -->
    <v-navigation-drawer app >
      <v-list dense>
        <v-list-item>
          <v-list-item-title class="text-h6">Menu</v-list-item-title>
        </v-list-item>

        <v-divider></v-divider>

        <v-list-item @click="goTo('plantes')">
          <v-list-item-icon><v-icon>mdi-leaf</v-icon></v-list-item-icon>
          <v-list-item-content>Plantes</v-list-item-content>
        </v-list-item>

        <v-list-item @click="goTo('messagerie')">
          <v-list-item-icon><v-icon>mdi-message</v-icon></v-list-item-icon>
          <v-list-item-content>Messagerie</v-list-item-content>
        </v-list-item>

        <v-list-item @click="goTo('historique')">
          <v-list-item-icon><v-icon>mdi-history</v-icon></v-list-item-icon>
          <v-list-item-content>Historique</v-list-item-content>
        </v-list-item>

        <v-list-item @click="logout">
          <v-list-item-icon><v-icon>mdi-logout</v-icon></v-list-item-icon>
          <v-list-item-content>Déconnexion</v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Contenu principal -->
    <v-main>
      <v-container>
        <v-row>
          <!-- Aperçu des plantes -->
          <v-col cols="12" md="8">
            <v-card>
              <v-card-title class="d-flex justify-space-between align-center">
                <span>Plantes à faire garder</span>
                <v-btn color="green" @click="goTo('ajouter-plant')">
                  <v-icon left>mdi-plus</v-icon>
                  Ajouter une plante
                </v-btn>
              </v-card-title>
              <v-container>
                <v-row>
                  <v-col v-for="plante in plantes" :key="plante.id" cols="12" md="6" lg="4">
                    <PlanteCard :plante="plante" @view-details="showDetails" @add-favorites="addToFavorites" />
                  </v-col>
                </v-row>
              </v-container>
            </v-card>
          </v-col>

          <!-- Raccourcis rapides -->
          <v-col cols="12" md="4">
            <v-card>
              <v-card-title>Accès rapide</v-card-title>
              <v-list>
                <v-list-item @click="goTo('messagerie')">
                  <v-list-item-icon><v-icon>mdi-message</v-icon></v-list-item-icon>
                  <v-list-item-content>Messagerie</v-list-item-content>
                </v-list-item>
                <v-list-item @click="goTo('historique')">
                  <v-list-item-icon><v-icon>mdi-history</v-icon></v-list-item-icon>
                  <v-list-item-content>Historique des plantes gardées</v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
