from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
import random
from django.conf import settings
import smtplib, ssl
from email.mime.text import MIMEText


# Muestra el formulario de login
def login_form(request):
    return render(request, "gestionLogin/login.html")

# Maneja el proceso de autenticación
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso")
            return redirect('index') 
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            

    return render(request, 'gestionLogin/login.html')

@login_required
def index(request):
    return render(request, "index.html")

User = get_user_model()

def registro_form(request):
    form = UserCreationForm()
    return render(request, 'gestionLogin/registro.html', {'form': form})


verification_codes = {}

def registro_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_type = request.POST['user_type']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if user_type == "":
            messages.error(request, "Debes seleccionar un tipo de usuario.")
            return redirect("registro_form")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('registro_form')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('registro_form')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect('registro_form')
        
                # Validar longitud de la contraseña
        '''if len(password1) < 8:
            messages.error(request, "❌ La contraseña debe tener al menos 8 caracteres.")
            return redirect('registro')'''
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            password=password1,
            is_active=False  # Usuario inactivo hasta verificar email
        )

        # Generar código de 6 dígitos
        codigo_verificacion = str(random.randint(100000, 999999))
        request.session["codigo_verificacion"] = codigo_verificacion  # Guardamos el código en sesión
        request.session["email_verificacion"] = email  # Guardamos el email en sesión
        request.session["password_temp"] = password1

        # Enviar correo electrónico con el código
        try:
            msg = MIMEText(f"Tu código de verificación es: {codigo_verificacion}")
            msg['Subject'] = "Código de verificación de WeStand"
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = email

            context = ssl._create_unverified_context()  # ⚠️ No verifica el certificado por problema con los certificados 

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls(context=context)
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print("Error al enviar el correo:", e)
            messages.error(request, "No se pudo enviar el correo.")


        messages.success(request, "Se ha enviado un código de verificación a tu correo.")
        return redirect('verificar_email', email=email)

    return render(request, 'gestionLogin/registro.html')

from django.contrib.auth import login, authenticate

def verificar_email_view(request, email):
    if request.method == "POST":
        codigo_ingresado = request.POST["codigo"]

        if codigo_ingresado == request.session.get("codigo_verificacion"):
            # Activar usuario
            try:
                user = User.objects.get(email=request.session.get("email_verificacion"))
                user.is_active = True
                user.save()

                # Iniciar sesión automáticamente
                user_autenticado = authenticate(request, username=user.username, password=request.session.get("password_temp"))
                if user_autenticado:
                    login(request, user_autenticado)
                    messages.success(request, "Verificación exitosa. Has iniciado sesión.")
                    return redirect("index")  # Redirigir al área de usuario

            except User.DoesNotExist:
                messages.error(request, "Hubo un error con la verificación. Intenta registrarte nuevamente.")
                return redirect("registro_form")
        else:
            messages.error(request, "Código incorrecto. Inténtalo nuevamente.")
            return redirect("verificar_email", email=email)

    return render(request, "gestionLogin/verificar_email.html", {"email": email})

