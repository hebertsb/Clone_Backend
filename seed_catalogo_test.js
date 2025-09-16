// Script para seed de catálogo (servicios/paquetes/destinos)
// Uso: node seed_catalogo_test.js
// Requiere: establecer la variable de entorno BASE_URL y ACCESS_TOKEN, por ejemplo:
// $env:BASE_URL = 'http://localhost:8000/api'; $env:ACCESS_TOKEN = 'Bearer ey...'; node seed_catalogo_test.js

const fetch = require('node-fetch');

const baseUrl = process.env.BASE_URL || 'http://localhost:8000/api';
const accessToken = process.env.ACCESS_TOKEN || '';

if (!accessToken) {
  console.error('ERROR: debes establecer ACCESS_TOKEN como variable de entorno (incluye "Bearer ")');
  process.exit(1);
}

async function post(path, body) {
  const res = await fetch(`${baseUrl}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': accessToken
    },
    body: JSON.stringify(body)
  });
  const json = await res.json().catch(() => ({}));
  return { status: res.status, json };
}

(async () => {
  console.log('Creando Categoria...');
  let r = await post('/categorias/', { nombre: 'Pruebas', descripcion: 'Categoria seed para pruebas' });
  console.log(r.status, r.json);
  const categoriaId = r.json.id || r.json.pk || 1;

  console.log('Creando Servicios...');
  r = await post('/servicios/', {
    tipo: 'TOUR',
    titulo: 'Tour prueba ciudad',
    descripcion: 'Tour de prueba para testing',
    duracion_min: 120,
    costo: '80.00',
    capacidad_max: 10,
    punto_encuentro: 'Plaza Test',
    visible_publico: true,
    categoria: categoriaId
  });
  console.log(r.status, r.json);
  const servicio1 = r.json.id || r.json.pk;

  r = await post('/servicios/', {
    tipo: 'ACTIVIDAD',
    titulo: 'Caminata test',
    descripcion: 'Actividad de prueba',
    duracion_min: 180,
    costo: '50.00',
    capacidad_max: 8,
    punto_encuentro: 'Entrada Test',
    visible_publico: true,
    categoria: categoriaId
  });
  console.log(r.status, r.json);
  const servicio2 = r.json.id || r.json.pk;

  console.log('Creando Destino...');
  r = await post('/destinos/', { nombre: 'Destino Test', dias: 3, descripcion: 'Destino seed' });
  console.log(r.status, r.json);
  const destinoId = r.json.id || r.json.pk;

  console.log('Creando Itinerario...');
  r = await post('/itinerarios/', { dia: 1, titulo: 'Día 1 - Test', actividades: ['Actividad A', 'Actividad B'] });
  console.log(r.status, r.json);
  const itinId = r.json.id || r.json.pk;

  console.log('Creando Paquete...');
  r = await post('/paquetes/', {
    nombre: 'Paquete Test',
    ubicacion: 'Ciudad Test',
    descripcion_corta: 'Paquete corto',
    descripcion_completa: 'Paquete completo para pruebas',
    calificacion: '4.5',
    numero_reseñas: 10,
    precio: '300.00',
    precio_original: '350.00',
    duracion: '3 días',
    max_personas: 6,
    dificultad: 'media',
    categoria: categoriaId,
    imagenes: ['https://example.com/img1.jpg'],
    destinos: [destinoId],
    itinerario: [itinId],
    incluido: ['Desayuno', 'Transporte'],
    no_incluido: ['Bebidas'],
    fechas_disponibles: ['2025-10-01T00:00:00Z'],
    descuento: '10.00'
  });
  console.log(r.status, r.json);

  console.log('Seed terminado.');
})();
