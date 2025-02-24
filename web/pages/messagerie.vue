<!-- Messagerie.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import BackButton from '@/components/buttons/BackButton.vue';

const router = useRouter();
const messageList = ref(null);

const messages = ref([
  { 
    id: 1, 
    auteur: "Alice",
    avatar: "/avatar-alice.jpg",
    texte: "Je peux garder votre ficus cette semaine.",
    timestamp: "2024-02-14T10:30:00",
    isMe: false
  },
  { 
    id: 2, 
    auteur: "Bob",
    avatar: "/avatar-bob.jpg",
    texte: "Super, merci Alice !",
    timestamp: "2024-02-14T10:35:00",
    isMe: false
  }
]);

const nouveauMessage = ref("");
const loading = ref(false);

const envoyerMessage = async () => {
  if (nouveauMessage.value.trim()) {
    loading.value = true;
    
    // Simuler un délai réseau
    await new Promise(resolve => setTimeout(resolve, 500));
    
    messages.value.push({
      id: messages.value.length + 1,
      auteur: "Moi",
      avatar: "/avatar-me.jpg",
      texte: nouveauMessage.value,
      timestamp: new Date().toISOString(),
      isMe: true
    });
    
    nouveauMessage.value = "";
    loading.value = false;
    scrollToBottom();
  }
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const scrollToBottom = () => {
  setTimeout(() => {
    if (messageList.value) {
      messageList.value.$el.scrollTop = messageList.value.$el.scrollHeight;
    }
  }, 50);
};

onMounted(() => {
  scrollToBottom();
});
</script>

<template>
  <v-container class="pa-4 fill-height">
    <div class="d-flex flex-column" style="height: 100%">
      <div class="d-flex align-center mb-4">
        <BackButton class="mr-4" />
        <h1 class="text-h4 font-weight-medium">Messagerie</h1>
      </div>

      <v-card class="flex-grow-1 d-flex flex-column" elevation="2">
        <v-list
          ref="messageList"
          class="flex-grow-1 bg-grey-lighten-4"
          style="overflow-y: auto"
        >
          <v-list-item
            v-for="msg in messages"
            :key="msg.id"
            :class="{ 'justify-end': msg.isMe }"
          >
            <div :class="{ 'd-flex flex-row-reverse': msg.isMe }">
              <v-avatar :color="msg.isMe ? 'primary' : 'grey-lighten-1'" class="mx-3">
                <v-img v-if="msg.avatar" :src="msg.avatar" alt="avatar"/>
                <span v-else class="text-h6 text-white">
                  {{ msg.auteur[0].toUpperCase() }}
                </span>
              </v-avatar>
              
              <div :class="{ 'text-right': msg.isMe }">
                <div class="text-caption text-grey">
                  {{ msg.auteur }} • {{ formatTime(msg.timestamp) }}
                </div>
                <v-card
                  :color="msg.isMe ? 'primary' : 'white'"
                  :class="{ 'text-white': msg.isMe }"
                  class="pa-2 mt-1"
                  elevation="1"
                  rounded="lg"
                >
                  {{ msg.texte }}
                </v-card>
              </div>
            </div>
          </v-list-item>
        </v-list>

        <v-divider></v-divider>

        <div class="pa-4">
          <v-form @submit.prevent="envoyerMessage">
            <div class="d-flex align-center">
              <v-text-field
                v-model="nouveauMessage"
                label="Écrire un message"
                variant="outlined"
                density="comfortable"
                hide-details
                class="mr-4"
                @keyup.enter="envoyerMessage"
              ></v-text-field>
              
              <v-btn
                color="primary"
                :loading="loading"
                :disabled="!nouveauMessage.trim()"
                @click="envoyerMessage"
              >
                <v-icon>mdi-send</v-icon>
              </v-btn>
            </div>
          </v-form>
        </div>
      </v-card>
    </div>
  </v-container>
</template>

<style scoped>
.v-list-item {
  min-height: auto;
  padding: 8px 16px;
}
</style>