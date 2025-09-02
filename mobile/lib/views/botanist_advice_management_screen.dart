import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/advice_provider.dart';
import '../widgets/advice_card.dart';
import '../models/advice.dart';
import 'base_page_botaniste.dart';

class BotanistAdviceManagementScreen extends StatefulWidget {
  const BotanistAdviceManagementScreen({Key? key}) : super(key: key);

  @override
  State<BotanistAdviceManagementScreen> createState() => _BotanistAdviceManagementScreenState();
}

class _BotanistAdviceManagementScreenState extends State<BotanistAdviceManagementScreen> 
    with TickerProviderStateMixin {
  late TabController _tabController;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        setState(() {
          _currentIndex = _tabController.index;
        });
      }
    });
    
    // Charger les données initiales
    _loadInitialData();
  }
  
  void _loadInitialData() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<AdviceProvider>(context, listen: false);
      provider.loadCurrentBotanistId();
      provider.loadStats();
      provider.loadPlantCaresToReview();
      provider.loadPlantCaresWithAdvice();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Forcer le rechargement quand on revient sur cette page
    _loadInitialData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BasePageBotaniste(
      currentIndex: 0, // Index pour "Gardes"
      body: Column(
        children: [
          // Header avec statistiques
          Container(
            color: Colors.green.shade50,
            padding: const EdgeInsets.all(16.0),
            child: Consumer<AdviceProvider>(
              builder: (context, provider, child) {
                final stats = provider.stats;
                if (stats == null) {
                  return const Center(child: CircularProgressIndicator());
                }
                
                return Column(
                  children: [
                    const Text(
                      'Conseils Botaniques',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatCard(
                            'À examiner',
                            stats.totalToReview.toString(),
                            Colors.orange,
                            Icons.assignment_turned_in,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _buildStatCard(
                            'Avec avis',
                            stats.totalReviewed.toString(),
                            Colors.green,
                            Icons.check_circle,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatCard(
                            'Urgent',
                            stats.urgentCount.toString(),
                            Colors.red,
                            Icons.warning,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _buildStatCard(
                            'À valider',
                            stats.pendingValidation.toString(),
                            Colors.blue,
                            Icons.verified_user,
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              },
            ),
          ),
          
          // Onglets
          Container(
            color: Colors.white,
            child: TabBar(
              controller: _tabController,
              labelColor: Colors.green,
              unselectedLabelColor: Colors.grey,
              indicatorColor: Colors.green,
              tabs: const [
                Tab(
                  icon: Icon(Icons.assignment),
                  text: 'À examiner',
                ),
                Tab(
                  icon: Icon(Icons.check_circle_outline),
                  text: 'Avis',
                ),
              ],
            ),
          ),
          
          // Contenu des onglets
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildToReviewTab(),
                _buildReviewedTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildToReviewTab() {
    return Consumer<AdviceProvider>(
      builder: (context, provider, child) {
        if (provider.isLoadingToReview) {
          return const Center(child: CircularProgressIndicator());
        }

        if (provider.plantCaresToReview.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.check_circle_outline,
                  size: 64,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                Text(
                  'Aucune garde à examiner',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.grey.shade600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Toutes les gardes ont reçu un avis botanique',
                  style: TextStyle(
                    color: Colors.grey.shade500,
                  ),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: provider.loadPlantCaresToReview,
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: provider.plantCaresToReview.length,
            itemBuilder: (context, index) {
              final plantCare = provider.plantCaresToReview[index];
              return AdviceCard(
                plantCare: plantCare,
                currentBotanistId: provider.currentBotanistId,
                onAdviceGiven: () async {
                  await provider.loadPlantCaresToReview();
                  await provider.loadPlantCaresWithAdvice();
                  await provider.loadStats();
                },
              );
            },
          ),
        );
      },
    );
  }

  Widget _buildReviewedTab() {
    return Consumer<AdviceProvider>(
      builder: (context, provider, child) {
        if (provider.isLoadingReviewed) {
          return const Center(child: CircularProgressIndicator());
        }

        if (provider.plantCaresWithAdvice.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.article_outlined,
                  size: 64,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                Text(
                  'Aucun avis donné',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.grey.shade600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Les avis botaniques apparaîtront ici',
                  style: TextStyle(
                    color: Colors.grey.shade500,
                  ),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: provider.loadPlantCaresWithAdvice,
          child: Column(
            children: [
              // Filtres
              Container(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<ValidationFilter>(
                        value: provider.validationFilter,
                        decoration: const InputDecoration(
                          labelText: 'Statut validation',
                          border: OutlineInputBorder(),
                          contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        ),
                        items: ValidationFilter.values.map((filter) {
                          return DropdownMenuItem(
                            value: filter,
                            child: Text(filter.displayName),
                          );
                        }).toList(),
                        onChanged: (filter) {
                          if (filter != null) {
                            provider.setValidationFilter(filter);
                          }
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    FilterChip(
                      label: const Text('Mes avis'),
                      selected: provider.myAdviceOnly,
                      onSelected: provider.toggleMyAdviceOnly,
                      selectedColor: Colors.green.shade100,
                    ),
                  ],
                ),
              ),
              
              // Liste des avis
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: provider.plantCaresWithAdvice.length,
                  itemBuilder: (context, index) {
                    final plantCare = provider.plantCaresWithAdvice[index];
                    return AdviceCard(
                      plantCare: plantCare,
                      showAdviceDetails: true,
                      showEditButton: true,
                      currentBotanistId: provider.currentBotanistId,
                      onAdviceGiven: () async {
                        await provider.loadPlantCaresWithAdvice();
                        await provider.loadStats();
                      },
                      onValidation: () async {
                        await provider.loadPlantCaresWithAdvice();
                        await provider.loadStats();
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
