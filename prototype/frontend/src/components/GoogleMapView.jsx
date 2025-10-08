import React from 'react';
import { GoogleMap, Marker, InfoWindow } from '@react-google-maps/api';

function GoogleMapView({ events, selectedEvent, onEventSelect, onClose, hoveredEventId, userLocation, isLoaded }) {

  const mapContainerStyle = {
    width: '100%',
    height: '100%'
  };

  // Centre de la carte - utilise userLocation en priorité
  const center = userLocation 
    ? { lat: userLocation.lat, lng: userLocation.lon }
    : { lat: 43.604, lng: 1.444 };

  console.log('🗺️ Centre de la carte:', center);
  console.log('📍 UserLocation:', userLocation);
  console.log('🎯 Événements:', events.length);

  // Créer des icônes personnalisées selon le contexte
  const getMarkerIcon = (event, isHovered = false) => {
    if (!isLoaded) return undefined;

    let color = '#9333ea'; // violet par défaut
    
    if (event.contexte.includes('seul')) {
      color = '#3b82f6'; // bleu
    } else if (event.contexte.includes('couple')) {
      color = '#ec4899'; // rose
    } else if (event.contexte.includes('groupe')) {
      color = '#8b5cf6'; // violet
    }

    // Taille selon survol - effet réduit
    const size = isHovered ? 50 : 46;
    const viewBox = isHovered ? '0 0 50 60' : '0 0 46 56';

    // SVG personnalisé pour le marqueur avec ombre intégrée
    const svg = `
      <svg width="${size}" height="${size + 10}" viewBox="${viewBox}" xmlns="http://www.w3.org/2000/svg">
        <!-- Ombre -->
        <ellipse cx="${size/2}" cy="${size + 6}" rx="${size/4}" ry="3" fill="rgba(0,0,0,0.3)"/>
        
        <!-- Pin principal -->
        <path d="M${size/2} 3C${size/2 - 8.284} 3 ${size/2 - 15} 9.716 ${size/2 - 15} 18c0 8.284 15 35 15 35s15-26.716 15-35c0-8.284-6.716-15-15-15z" 
              fill="${color}" stroke="rgba(0,0,0,0.2)" stroke-width="1"/>
        
        <!-- Cercle blanc -->
        <circle cx="${size/2}" cy="18" r="${isHovered ? 10 : 9}" fill="white"/>
        
        <!-- Score -->
        <text x="${size/2}" y="23" text-anchor="middle" font-size="${isHovered ? 12 : 11}" font-weight="bold" fill="${color}">
          ${event.score}
        </text>
      </svg>
    `;

    return {
      url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
      scaledSize: new window.google.maps.Size(size, size + 10),
      anchor: new window.google.maps.Point(size/2, size + 7)
    };
  };

  if (!isLoaded) {
    return (
      <div style={{ 
        width: '100%', 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f3f4f6'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #9333ea',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }} />
          <p style={{ color: '#6b7280', fontSize: '14px' }}>Chargement de la carte...</p>
        </div>
      </div>
    );
  }

  return (
    <GoogleMap
      key={`map-${center.lat}-${center.lng}`}
      mapContainerStyle={mapContainerStyle}
      center={center}
      zoom={13}
      options={{
        styles: [
          {
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
          }
        ],
        disableDefaultUI: false,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true
      }}
    >
        {isLoaded && events.map((event) => {
          const isHovered = hoveredEventId === event.id;
          return (
            <Marker
              key={event.id}
              position={{ lat: event.latitude, lng: event.longitude }}
              onClick={() => onEventSelect(event)}
              icon={getMarkerIcon(event, isHovered)}
            />
          );
        })}

        {/* Marqueur position utilisateur */}
        {userLocation && (
          <Marker
            position={{ lat: userLocation.lat, lng: userLocation.lon }}
            icon={{
              path: window.google.maps.SymbolPath.CIRCLE,
              fillColor: '#4285F4',
              fillOpacity: 1,
              strokeColor: '#ffffff',
              strokeWeight: 3,
              scale: 10,
            }}
            title="Votre position"
          />
        )}

        {selectedEvent && (
          <InfoWindow
            position={{ 
              lat: selectedEvent.latitude, 
              lng: selectedEvent.longitude 
            }}
            onCloseClick={onClose}
          >
            <div style={{ maxWidth: '250px', padding: '8px' }}>
              <h3 style={{ 
                margin: '0 0 8px 0', 
                fontSize: '16px', 
                fontWeight: 'bold',
                color: '#1f2937'
              }}>
                {selectedEvent.nom}
              </h3>
              
              <p style={{ 
                margin: '0 0 12px 0', 
                fontSize: '14px',
                color: '#6b7280' 
              }}>
                {selectedEvent.description}
              </p>

              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                marginBottom: '8px',
                fontSize: '13px'
              }}>
                <span style={{ fontWeight: 'bold' }}>⭐ {selectedEvent.qualite}/5</span>
                <span style={{ color: '#9ca3af' }}>({selectedEvent.nbAvis} avis)</span>
              </div>

              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                marginBottom: '8px',
                fontSize: '13px'
              }}>
                <span>🕐 {selectedEvent.horaire}</span>
                <span style={{ fontWeight: 'bold', color: '#9333ea' }}>{selectedEvent.prix}</span>
              </div>

              <div style={{ 
                display: 'flex', 
                gap: '8px',
                marginTop: '12px' 
              }}>
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${selectedEvent.latitude},${selectedEvent.longitude}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  style={{
                    flex: 1,
                    padding: '8px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '8px',
                    fontSize: '12px',
                    fontWeight: '600',
                    textAlign: 'center',
                    cursor: 'pointer'
                  }}
                >
                  📍 Itinéraire
                </a>
                
                {selectedEvent.urlSite && (
                  <a
                    href={selectedEvent.urlSite}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    style={{
                      flex: 1,
                      padding: '8px',
                      backgroundColor: '#9333ea',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '8px',
                      fontSize: '12px',
                      fontWeight: '600',
                      textAlign: 'center',
                      cursor: 'pointer'
                    }}
                  >
                    🌐 Site web
                  </a>
                )}
              </div>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
  );
}

export default GoogleMapView;