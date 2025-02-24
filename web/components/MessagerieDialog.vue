<template>
    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span class="text-h6">Messagerie</span>
          <v-btn icon @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
  
        <v-divider></v-divider>
  
        <!-- Zone des messages -->
        <v-card-text class="chat-box">
          <div v-for="message in messages" :key="message.id" class="d-flex mb-2" :class="message.sender === 'Moi' ? 'justify-end' : 'justify-start'">
            <v-chip
              :color="message.sender === 'Moi' ? 'primary' : 'grey'"
              dark
              class="chat-message"
            >
              <strong>{{ message.sender }}:</strong> {{ message.text }}
            </v-chip>
          </div>
        </v-card-text>
  
        <v-divider></v-divider>
  
        <!-- Champ de saisie du message -->
        <v-card-actions>
          <v-text-field
            v-model="newMessage"
            label="Écrire un message..."
            variant="outlined"
            dense
            class="flex-grow-1"
            @keyup.enter="sendMessage"
          ></v-text-field>
          <v-btn icon color="primary" @click="sendMessage">
            <v-icon>mdi-send</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const dialog = ref(false);
  const newMessage = ref('');
  const messages = ref([
    { id: 1, sender: 'Bot', text: 'Salut ! Comment puis-je t’aider ?' },
    { id: 2, sender: 'Moi', text: 'J’ai une question sur l’arrosage des plantes.' },
    { id: 3, sender: 'Bot', text: 'Bien sûr ! Quelle plante veux-tu arroser ?' }
  ]);
  
  const sendMessage = () => {
    if (newMessage.value.trim() === '') return;
  
    messages.value.push({ id: Date.now(), sender: 'Moi', text: newMessage.value });
    newMessage.value = '';
  
    // Réponse automatique (simulation)
    setTimeout(() => {
      messages.value.push({ id: Date.now(), sender: 'Bot', text: 'Bonne idée ! N’oublie pas d’arroser régulièrement. 🌱' });
    }, 1000);
  };
  </script>
  
  <style scoped>
  .chat-box {
    max-height: 300px;
    overflow-y: auto;
    padding: 10px;
  }
  .chat-message {
    max-width: 75%;
    word-wrap: break-word;
  }
  </style>
  