<script setup>
import { ref } from 'vue';
import EmailModal from '@/components/modals/EmailModal.vue';
import UsernameModal from '@/components/modals/UsernameModal.vue';
import FullNameModal from '@/components/modals/FullNameModal.vue';
import PhoneModal from '@/components/modals/PhoneModal.vue';
import CityModal from '@/components/modals/CityModal.vue';
import PasswordModal from '@/components/modals/PasswordModal.vue';
import BackButton from '@/components/buttons/BackButton.vue';

const email = ref('user@example.com');
const username = ref('username123');
const fullName = ref('John Doe');
const phoneNumber = ref('123-456-7890');
const city = ref('Paris');
const avatar = ref(null);

const emailModalVisible = ref(false);
const usernameModalVisible = ref(false);
const fullNameModalVisible = ref(false);
const phoneModalVisible = ref(false);
const cityModalVisible = ref(false);
const passwordModalVisible = ref(false);

// Open Modal functions
const openEmailModal = () => emailModalVisible.value = true;
const openUsernameModal = () => usernameModalVisible.value = true;
const openFullNameModal = () => fullNameModalVisible.value = true;
const openPhoneModal = () => phoneModalVisible.value = true;
const openCityModal = () => cityModalVisible.value = true;
const openPasswordModal = () => passwordModalVisible.value = true;

const logout = () => {
  console.log('Déconnexion...');
  // Logique de déconnexion ici
};

const uploadAvatar = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      avatar.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};
</script>

<template>
  <v-container class="pa-4">
    <div class="d-flex align-center mb-6">
      <BackButton class="mr-4" />
      <h1 class="text-h4 font-weight-medium">Paramètres du compte</h1>
    </div>

    <v-row>
      <!-- Section Profil -->
      <v-col cols="12" md="4">
        <v-card class="mb-4" elevation="2">
          <v-card-text class="text-center">
            <v-avatar size="150" color="grey-lighten-2" class="mb-4">
              <v-img v-if="avatar" :src="avatar" cover />
              <span v-else class="text-h3">{{ fullName[0]?.toUpperCase() }}</span>
              <v-btn
                color="green"
                size="small"
                icon
                density="compact"
                class="d-flex justify-center align-center"
                @click="$refs.avatarInput.click()"
              >
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
            </v-avatar>
            <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="uploadAvatar"
            />
            <h2 class="text-h5 mb-2">{{ fullName }}</h2>
            <p class="text-body-1 text-grey">{{ username }}</p>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Section Informations -->
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-text>
            <h3 class="text-h6 mb-4">Informations personnelles</h3>
            
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-3">mdi-account</v-icon>
                </template>
                <v-list-item-title>Nom complet</v-list-item-title>
                <v-list-item-subtitle>{{ fullName }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    variant="text"
                    color="primary"
                    @click="openFullNameModal"
                  >
                    Modifier
                  </v-btn>
                </template>
              </v-list-item>

              <v-divider class="my-2"></v-divider>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-3">mdi-at</v-icon>
                </template>
                <v-list-item-title>Nom d'utilisateur</v-list-item-title>
                <v-list-item-subtitle>{{ username }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    variant="text"
                    color="primary"
                    @click="openUsernameModal"
                  >
                    Modifier
                  </v-btn>
                </template>
              </v-list-item>

              <v-divider class="my-2"></v-divider>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-3">mdi-email</v-icon>
                </template>
                <v-list-item-title>Email</v-list-item-title>
                <v-list-item-subtitle>{{ email }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    variant="text"
                    color="primary"
                    @click="openEmailModal"
                  >
                    Modifier
                  </v-btn>
                </template>
              </v-list-item>

              <v-divider class="my-2"></v-divider>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-3">mdi-phone</v-icon>
                </template>
                <v-list-item-title>Téléphone</v-list-item-title>
                <v-list-item-subtitle>{{ phoneNumber }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    variant="text"
                    color="primary"
                    @click="openPhoneModal"
                  >
                    Modifier
                  </v-btn>
                </template>
              </v-list-item>

              <v-divider class="my-2"></v-divider>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-3">mdi-city</v-icon>
                </template>
                <v-list-item-title>Ville</v-list-item-title>
                <v-list-item-subtitle>{{ city }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    variant="text"
                    color="primary"
                    @click="openCityModal"
                  >
                    Modifier
                  </v-btn>
                </template>
              </v-list-item>

              <v-divider class="my-2"></v-divider>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-3">mdi-lock</v-icon>
                </template>
                <v-list-item-title>Mot de passe</v-list-item-title>
                <v-list-item-subtitle>••••••••</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    variant="text"
                    color="primary"
                    @click="openPasswordModal"
                  >
                    Modifier
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>

            <v-divider class="my-4"></v-divider>

            <div class="d-flex justify-center">
              <v-btn
                color="error"
                variant="elevated"
                prepend-icon="mdi-logout"
                @click="logout"
              >
                Déconnexion
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Modals -->
    <EmailModal v-model="emailModalVisible" />
    <UsernameModal v-model="usernameModalVisible" />
    <FullNameModal v-model="fullNameModalVisible" />
    <PhoneModal v-model="phoneModalVisible" />
    <CityModal v-model="cityModalVisible" />
    <PasswordModal v-model="passwordModalVisible" />
  </v-container>
</template>

<style scoped>
.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  transform: translate(25%, 25%);
}

.v-list-item {
  min-height: 64px;
}
</style>