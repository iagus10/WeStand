def aumentar_experiencia_y_nivel(usuario, experiencia_ganada=50):
    usuario.experiencia += experiencia_ganada

    # Puedes personalizar este sistema como quieras
    niveles = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 800,
        6: 1200,
        7: 1700,
        8: 2300,
        9: 3000,
        10: 3800
    }

    # Determinar el nivel actual según la experiencia acumulada
    for nivel, xp_necesaria in sorted(niveles.items(), reverse=True):
        if usuario.experiencia >= xp_necesaria:
            usuario.nivel = nivel
            break

    usuario.save()