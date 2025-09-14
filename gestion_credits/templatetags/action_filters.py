from django import template
import json

register = template.Library()

@register.filter
def format_json(value):
    """Formate les données JSON pour l'affichage dans les modals"""
    if not value:
        return "Aucune donnée"
    
    try:
        if isinstance(value, str):
            # Si c'est déjà une chaîne JSON, la parser puis la reformater
            parsed = json.loads(value)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        else:
            # Si c'est un objet Python, le convertir en JSON formaté
            return json.dumps(value, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        # En cas d'erreur, retourner la valeur brute
        return str(value)

@register.filter
def truncate_json(value, length=200):
    """Tronque les données JSON longues pour l'affichage"""
    if not value:
        return "Aucune donnée"
    
    formatted = format_json(value)
    if len(formatted) > length:
        return formatted[:length] + "..."
    return formatted
