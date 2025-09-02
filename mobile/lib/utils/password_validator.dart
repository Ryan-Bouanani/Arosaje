class PasswordValidationResult {
  final bool isValid;
  final List<String> errors;

  PasswordValidationResult({required this.isValid, required this.errors});
}

class PasswordValidator {
  /// Valide la politique de mot de passe CNIL :
  /// - Minimum 14 caractères
  /// - Au moins une majuscule
  /// - Au moins une minuscule
  /// - Au moins un chiffre
  /// - Caractères spéciaux optionnels (non obligatoires)
  static PasswordValidationResult validateCNILPolicy(String password) {
    List<String> errors = [];

    // Vérification de la longueur minimum (14 caractères)
    if (password.length < 14) {
      errors.add("Minimum 14 caractères requis");
    }

    // Vérification de la présence d'au moins une majuscule
    if (!RegExp(r'[A-Z]').hasMatch(password)) {
      errors.add("Ajoutez au moins une majuscule");
    }

    // Vérification de la présence d'au moins une minuscule
    if (!RegExp(r'[a-z]').hasMatch(password)) {
      errors.add("Ajoutez au moins une minuscule");
    }

    // Vérification de la présence d'au moins un chiffre
    if (!RegExp(r'[0-9]').hasMatch(password)) {
      errors.add("Ajoutez au moins un chiffre");
    }

    bool isValid = errors.isEmpty;
    return PasswordValidationResult(isValid: isValid, errors: errors);
  }

  /// Retourne une description des exigences de mot de passe
  static String getPolicyDescription() {
    return "Le mot de passe doit contenir :\n"
           "• Au minimum 14 caractères\n"
           "• Au moins une majuscule (A-Z)\n"
           "• Au moins une minuscule (a-z)\n"
           "• Au moins un chiffre (0-9)";
  }
}
