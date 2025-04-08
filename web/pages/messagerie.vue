<script setup>
import { ref, onMounted } from 'vue';
import BackButton from '@/components/buttons/BackButton.vue';
import { mdiSend, mdiLeaf, mdiInformation, mdiImage } from '@mdi/js';
import { ApiService } from '@/services/api';

// États et données
const messages = ref([
  { id: 1, sender: 'botaniste', content: 'Bonjour, que puis-je faire pour vous aujourd\'hui ?', timestamp: '2024-02-25 10:00', isTyping: false }
]);

const botanisteInfo = ref({ nom: 'Dr. Claire Dubois', specialite: 'Plantes méditerranéennes et aromatiques', experience: '15 ans', photo: '/assets/botaniste.jpg' });
const newMessage = ref('');
const showBotanisteInfo = ref(false);
const isLoading = ref(false);
const messageScrollRef = ref(null);
const selectedPlant = ref(null);
const attachmentOptions = [
  { icon: mdiImage, title: 'Photo', action: () => alert('Fonctionnalité d\'envoi de photo à implémenter') },
  { icon: mdiLeaf, title: 'Identifier plante', action: () => alert('Fonctionnalité d\'identification de plante à implémenter') }
];

// Liste des plantes simple pour les réponses (noms sans accents)
const plants = ref([]);

// Liste détaillée des plantes (à charger depuis l'API)
const plantes = ref([]);

// Fonction pour récupérer les plantes depuis l'API
const fetchPlants = async () => {
  const response = await ApiService.getPlants();
  if (response.success && Array.isArray(response.data)) {
    // Mettre à jour la liste détaillée des plantes
    plantes.value = response.data.map(plant => ({
      ...plant,
      photo: ApiService.buildPhotoUrl(plant.photo) // Ajout de l'URL complète de l'image
    }));
    
    // Mettre à jour la liste simple des noms de plantes pour les réponses
    plants.value = response.data.map(plant => {
      // Normaliser le nom (enlever les accents, mettre en minuscule)
      return plant.nom.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    });
  } else {
    console.error('Erreur de récupération des plantes:', response.error);
  }
};

// Fonctions
const getTimestamp = () => new Date().toLocaleString('fr-FR', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' });

const scrollToBottom = () => {
  setTimeout(() => {
    if (messageScrollRef.value) messageScrollRef.value.scrollTop = messageScrollRef.value.scrollHeight;
  }, 100);
};

const selectPlant = (plante) => {
  selectedPlant.value = plante;
  newMessage.value = `Pouvez-vous me donner des conseils sur ${plante.nom} ?`;
};

// Réponse spécifique en fonction de la plante
const generateResponse = (question) => {
  // Recherche de la plante dans la question
  const normalizedQuestion = question.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  
  // Chercher dans la liste des noms de plantes
  const plant = plants.value.find(p => normalizedQuestion.includes(p));
  
  // Si une plante est trouvée
  if (plant) {
    // Trouver la plante correspondante dans la liste détaillée
    const planteDetail = plantes.value.find(p => 
      p.nom.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") === plant
    );
    
    if (planteDetail) {
      const nom = planteDetail.nom;
      
      switch (plant) {
        case 'chrysantheme':
          return `Le ${nom} préfère un sol bien drainé et un ensoleillement direct. Arrosez régulièrement, mais évitez l\'excès d\'eau.`;
        case 'jasmin':
          return `Le ${nom} aime le soleil et nécessite un sol bien drainé. Arrosez-le modérément et évitez les excès d\'eau qui peuvent faire pourrir les racines.`;
        case 'lavande':
          return `La ${nom} préfère un sol sec. Arrosez-la seulement quand le sol est complètement sec, environ une fois par semaine en été et une fois par mois en hiver.`;
        case 'lys':
          return `Les ${nom} préfèrent un sol riche et bien drainé. Arrosez-les modérément, mais veillez à ne pas laisser l\'eau stagner.`;
        case 'marguerite':
          return `Les ${nom}s aiment le soleil et un sol bien drainé. Arrosez-les modérément en évitant les excès d\'eau.`;
        case 'orchidee':
          return `Les ${nom}s nécessitent un environnement humide avec un arrosage léger. Arrosez-les une fois par semaine en été et réduisez l\'arrosage en hiver.`;
        case 'pivoine':
          return `Les ${nom}s aiment un sol profond et bien drainé. Arrosez-les régulièrement pendant la croissance, mais évitez l\'excès d\'eau.`;
        case 'rose':
          return `Les ${nom}s préfèrent un sol légèrement acide, riche et bien drainé. Arrosez-les régulièrement, mais évitez de mouiller les feuilles.`;
        case 'tournesol':
          return `Les ${nom}s ont besoin de plein soleil et d\'un sol bien drainé. Arrosez-les fréquemment en été, surtout pendant la floraison.`;
        case 'tulipe':
          return `Les ${nom}s préfèrent un sol léger et bien drainé. Arrosez-les modérément, mais évitez l\'excès d\'eau pour prévenir la pourriture des bulbes.`;
        default:
          return `Pour ${nom}, je vous recommande de vérifier les besoins spécifiques d\'arrosage, d\'exposition et de sol. N\'hésitez pas à me donner plus de détails pour une réponse plus précise.`;
      }
    }
  }

  if (normalizedQuestion.includes('arrosage')) {
    return 'Pour l\'arrosage, la règle générale est de vérifier l\'humidité du sol avant d\'arroser. La plupart des plantes préfèrent un sol qui sèche légèrement entre les arrosages.';
  } else if (normalizedQuestion.includes('engrais') || normalizedQuestion.includes('fertilisant')) {
    return 'Utilisez un engrais équilibré pendant la saison de croissance (printemps/été). Réduisez ou arrêtez la fertilisation en automne et en hiver.';
  }

  return 'Merci pour votre question. Pour vous donner les meilleurs conseils, pourriez-vous me préciser le type de plante dont vous parlez et son environnement actuel (intérieur/extérieur, exposition au soleil, etc.) ? Vous pouvez également sélectionner une plante dans la liste à droite.';
};

const sendMessage = () => {
  if (!newMessage.value.trim()) return;
  
  const userQuestion = newMessage.value;
  messages.value.push({ id: messages.value.length + 1, sender: 'utilisateur', content: userQuestion, timestamp: getTimestamp(), isTyping: false });
  newMessage.value = '';
  
  isLoading.value = true;
  messages.value.push({ id: messages.value.length + 1, sender: 'botaniste', content: '', timestamp: getTimestamp(), isTyping: true });
  scrollToBottom();
  
  setTimeout(() => {
    const typingIndex = messages.value.findIndex(m => m.isTyping);
    if (typingIndex !== -1) {
      messages.value[typingIndex] = {
        ...messages.value[typingIndex],
        content: generateResponse(userQuestion),
        isTyping: false
      };
    }
    isLoading.value = false;
    scrollToBottom();
  }, 1500);
};

// Charger les plantes au montage du composant
onMounted(() => {
  fetchPlants();
  scrollToBottom();
});
</script>

<template>
  <BackButton class="mr-4" />
  <div class="messagerie-container">
    <div class="header-container">
      <div class="header">
        <div class="botaniste-header" @click="showBotanisteInfo = !showBotanisteInfo">
          <div class="avatar">
            <v-avatar size="40">
              <v-img :src="botanisteInfo.photo" alt="Avatar du botaniste">
                <template v-slot:placeholder>
                  <div class="avatar-placeholder"><v-icon :icon="mdiLeaf"></v-icon></div>
                </template>
              </v-img>
            </v-avatar>
            <div class="online-indicator"></div>
          </div>
          <div class="botaniste-info">
            <h2>{{ botanisteInfo.nom }}</h2>
            <p>{{ botanisteInfo.specialite }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showBotanisteInfo" class="botaniste-popup">
      <div class="popup-header">
        <h3>Votre Botaniste</h3>
        <v-btn icon size="small" @click="showBotanisteInfo = false"><v-icon>mdi-close</v-icon></v-btn>
      </div>
      <div class="popup-content">
        <v-img :src="botanisteInfo.photo" height="120" width="120" class="popup-avatar"></v-img>
        <h3>{{ botanisteInfo.nom }}</h3>
        <p><strong>Spécialité:</strong> {{ botanisteInfo.specialite }}</p>
        <p><strong>Expérience:</strong> {{ botanisteInfo.experience }}</p>
        <p>Disponible du lundi au vendredi de 9h à 18h</p>
        <div class="botaniste-tags">
          <span class="tag">Plantes d'intérieur</span>
          <span class="tag">Herbes aromatiques</span>
          <span class="tag">Jardinage bio</span>
        </div>
      </div>
    </div>

    <div class="messagerie-body">
      <div class="messages-container" ref="messageScrollRef">
        <div v-for="message in messages" :key="message.id" 
             class="message-wrapper" :class="message.sender">
          <div class="message" :class="{ 'typing': message.isTyping }">
            <div v-if="message.isTyping" class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
            <template v-else>{{ message.content }}</template>
            <div class="message-timestamp">{{ message.timestamp }}</div>
          </div>
        </div>
      </div>

      <!-- Plantes list on the right -->
      <div class="plants-list">
        <h3>Choisissez une plante</h3>
        <div class="plants-container">
          <div v-for="plante in plantes" :key="plante.id" class="plant-item" 
               @click="selectPlant(plante)" :class="{ 'selected': selectedPlant && selectedPlant.id === plante.id }">
            <v-avatar size="48" class="plant-avatar">
              <v-img :src="plante.photo" alt="Plante">
                <template v-slot:placeholder>
                  <div class="plant-placeholder"><v-icon :icon="mdiLeaf"></v-icon></div>
                </template>
              </v-img>
            </v-avatar>
            <div class="plant-details">
              <p class="plant-name">{{ plante.nom }}</p>
              <div class="plant-health">
                <div class="health-bar">
                 
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="input-container">
      <div class="attachment-options">
        <v-btn v-for="(option, index) in attachmentOptions" :key="index" 
               icon variant="text" color="green-darken-1" @click="option.action">
          <v-icon :icon="option.icon"></v-icon>
          <v-tooltip activator="parent" location="top">{{ option.title }}</v-tooltip>
        </v-btn>
      </div>

      <div class="message-input">
        <v-textarea v-model="newMessage" placeholder="Posez votre question sur vos plantes..."
                  rows="1" auto-grow hide-details density="compact"
                  @keydown.enter.prevent="sendMessage"></v-textarea>
        <v-btn icon color="green-darken-2" @click="sendMessage" 
              :disabled="!newMessage.trim() || isLoading" class="send-button">
          <v-icon>mdi-send</v-icon> 
        </v-btn>
      </div>
    </div>
  </div>
</template>

<style scoped>
.messagerie-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1000px;
  margin: 0 auto;
  background-color: #e7efef;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

.header-container {
  background: linear-gradient(135deg, #4caf50, #2e7d32);
  color: white;
  padding: 12px 16px;
  position: relative;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-left: 36px;
}

.botaniste-header {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.avatar {
  position: relative;
  margin-right: 12px;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e8f5e9;
  width: 100%;
  height: 100%;
}

.online-indicator {
  width: 10px;
  height: 10px;
  background-color: #4caf50;
  border-radius: 50%;
  border: 2px solid white;
  position: absolute;
  bottom: 0;
  right: 0;
}

.botaniste-info h2 {
  font-size: 16px;
  margin: 0;
  font-weight: 600;
}

.botaniste-info p {
  font-size: 12px;
  margin: 0;
  opacity: 0.9;
}

.info-button { color: white; }

.messagerie-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%234caf50' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.message-wrapper {
  display: flex;
  margin-bottom: 16px;
}

.message-wrapper.botaniste {
  justify-content: flex-start;
}

.message-wrapper.utilisateur {
  justify-content: flex-end;
}

.message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-wrapper.botaniste .message {
  background-color: #e8f5e9;
  border-bottom-left-radius: 4px;
  color: #1b5e20;
}

.message-wrapper.utilisateur .message {
  background-color: #e3f2fd;
  border-bottom-right-radius: 4px;
  color: #0d47a1;
}

.message-timestamp {
  font-size: 10px;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 24px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  border-radius: 50%;
  background-color: #4caf50;
  margin: 0 1px;
  display: inline-block;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.4s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.input-container {
  background-color: white;
  padding: 8px 16px;
  border-top: 1px solid #e0e0e0;
}

.attachment-options {
  display: flex;
  padding: 4px 0;
}

.message-input {
  display: flex;
  align-items: flex-end;
  background-color: #f1f3f4;
  border-radius: 24px;
  padding: 0 8px 0 16px;
}

.message-input .v-textarea {
  background-color: transparent;
  padding: 8px 0;
}

.send-button {
  margin-left: 8px;
  margin-bottom: 4px;
}

.botaniste-popup {
  position: absolute;
  top: 70px;
  right: 16px;
  background: white;
  border-radius: 12px;
  width: 300px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
}

.popup-header {
  background: linear-gradient(135deg, #4caf50, #2e7d32);
  color: white;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-header h3 {
  margin: 0;
  font-size: 16px;
}

.popup-content {
  padding: 16px;
  text-align: center;
}

.popup-avatar {
  border-radius: 50%;
  margin: 0 auto 16px;
  border: 3px solid #e8f5e9;
}

.popup-content h3 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #2e7d32;
}

.popup-content p {
  margin: 4px 0;
  font-size: 14px;
  text-align: left;
}

.botaniste-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 12px;
}

.tag {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 4px 8px;
  border-radius: 16px;
  font-size: 12px;
  margin: 4px;
}

/* Plants list styles */
.plants-list {
  width: 240px;
  background-color: white;
  border-left: 1px solid #e0e0e0;
  overflow-y: auto;
  padding: 16px;
}

.plants-list h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #2e7d32;
  font-size: 16px;
  text-align: center;
}

.plants-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.plant-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.plant-item:hover {
  background-color: #f1f8e9;
}

.plant-item.selected {
  background-color: #e8f5e9;
  border: 1px solid #4caf50;
}

.plant-avatar {
  margin-right: 12px;
}

.plant-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e8f5e9;
  width: 100%;
  height: 100%;
}

.plant-details {
  flex: 1;
}

.plant-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: #2e7d32;
}

.plant-health {
  width: 100%;
}

.health-bar {
  height: 4px;
  background-color: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.health-fill {
  height: 100%;
  transition: width 0.3s ease;
}

@media (max-width: 768px) {
  .messagerie-container {
    height: 100vh;
    max-width: 100%;
    border-radius: 0;
  }
  
  .messagerie-body {
    flex-direction: column;
  }
  
  .plants-list {
    width: 100%;
    height: 120px;
    border-left: none;
    border-top: 1px solid #e0e0e0;
  }
  
  .plants-container {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 8px;
  }
  
  .plant-item {
    flex-direction: column;
    width: 80px;
    text-align: center;
  }
  
  .plant-avatar {
    margin-right: 0;
    margin-bottom: 8px;
  }
}
</style>