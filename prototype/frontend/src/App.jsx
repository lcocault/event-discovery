import React, { useState, useEffect } from 'react';
import { MapPin, Users, User, Heart, Clock, Sun, List, Map, Filter, X, Navigation, Star, History, Globe, Coffee, Camera, Utensils, Shuffle, Accessibility, Calendar, Edit2, CloudRain, Cloud } from 'lucide-react';
import { useLoadScript } from '@react-google-maps/api';
import GoogleMapView from './components/GoogleMapView';

const API_URL = 'http://localhost:8000';

const mockEvents = [{
  id: 1, nom: "Concert Jazz au Bikini", categorie: "Concert", distance: 1.2, horaire: "20:30",
  heureFermeture: "23:30", score: 95, contexte: ["couple", "groupe"], qualite: 4.5, nbAvis: 328,
  prix: "25€", description: "Soirée jazz avec quartet local", latitude: 43.5896, longitude: 1.4012,
  urlSite: "https://www.lebikini.com", tags: ["afterwork", "touriste"], pmr: false,
  imageUrl: "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800"
}];

const quickFilters = [
  { id: 'afterwork', label: 'Afterwork', icon: Coffee, tag: 'afterwork', color: 'from-amber-500 to-orange-600', time: '2 min' },
  { id: 'pluie', label: 'Il pleut !', icon: CloudRain, tag: 'pluie', color: 'from-blue-500 to-indigo-600', time: '3 min' },
  { id: 'touriste', label: 'Touriste', icon: Camera, tag: 'touriste', color: 'from-pink-500 to-rose-600', time: '5 min' },
  { id: 'faim', label: "J'ai faim !", icon: Utensils, tag: 'faim', color: 'from-emerald-500 to-teal-600', time: '1 min' },
  { id: 'hazard', label: 'Hasard', icon: Shuffle, tag: 'hazard', color: 'from-purple-500 to-violet-600', time: '??? min' },
  { id: 'pmr', label: 'PMR', icon: Accessibility, tag: 'pmr', color: 'from-indigo-500 to-blue-600', time: 'OK' }
];

function App() {
  const [page, setPage] = useState('home');
  const [isSearching, setIsSearching] = useState(false);
  const [viewMode, setViewMode] = useState('list');
  const [contextFilters, setContextFilters] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedQuickFilter, setSelectedQuickFilter] = useState(null);
  const [selectedMapEvent, setSelectedMapEvent] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState('Toulouse Centre');
  const [currentDate, setCurrentDate] = useState(new Date().toISOString().split('T')[0]);
  const [currentCoordinates, setCurrentCoordinates] = useState({ lat: 43.604, lon: 1.444 });
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [showDateModal, setShowDateModal] = useState(false);
  const [tempLocation, setTempLocation] = useState('');
  const [tempDate, setTempDate] = useState('');
  const [hoveredEventId, setHoveredEventId] = useState(null);
  const [isGeolocating, setIsGeolocating] = useState(false);
  const [hasGeolocated, setHasGeolocated] = useState(false);
  const [meteo, setMeteo] = useState({ temperature: 22, pluie: false, description: 'Ensoleillé' });
  const [loadingMeteo, setLoadingMeteo] = useState(false);

  const { isLoaded: isMapLoaded } = useLoadScript({
  googleMapsApiKey: process.env.REACT_APP_GOOGLE_API_KEY
  });

  useEffect(() => {
    if (!hasGeolocated && navigator.geolocation) {
      handleGeolocate();
    }
  }, []);

  const loadMeteo = async (lat, lon) => {
    setLoadingMeteo(true);
    try {
      const response = await fetch(`${API_URL}/meteo?lat=${lat}&lon=${lon}`);
      const data = await response.json();
      setMeteo(data);
    } catch (error) {
      console.error('Erreur météo:', error);
    }
    setLoadingMeteo(false);
  };

  const handleGeolocate = () => {
    if (!navigator.geolocation) return;
    setIsGeolocating(true);
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        
        try {
          const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lon}&key=${process.env.REACT_APP_GOOGLE_API_KEY}`;
          const response = await fetch(geocodeUrl);
          const data = await response.json();
          
          if (data.results && data.results.length > 0) {
            let address = data.results[0].formatted_address;
            for (let result of data.results) {
              if (result.types.includes('locality') || result.types.includes('political')) {
                address = result.formatted_address;
                break;
              }
            }
            setCurrentLocation(address);
            setCurrentCoordinates({ lat, lon });
            setHasGeolocated(true);
            loadMeteo(lat, lon);
            if (page === 'results') loadEvents();
          }
        } catch (error) {
          console.error('Erreur géocodage:', error);
        }
        setIsGeolocating(false);
      },
      (error) => {
        console.log('Géolocalisation refusée:', error.message);
        setIsGeolocating(false);
        setHasGeolocated(true);
        loadMeteo(43.604, 1.444);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
  };

  const handleSearch = (quickFilter = null) => {
    setIsSearching(true);
    setSelectedQuickFilter(quickFilter);
    setTimeout(() => {
      setIsSearching(false);
      setPage('results');
    }, 2000);
  };

  const toggleContextFilter = (context) => {
    setContextFilters(prev => 
      prev.includes(context) ? prev.filter(c => c !== context) : [...prev, context]
    );
  };

  const loadEvents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        lat: currentCoordinates.lat.toString(),
        lon: currentCoordinates.lon.toString()
      });
      if (selectedQuickFilter) params.append('quick_filter', selectedQuickFilter);
      if (currentDate) params.append('date', currentDate);
      
      const response = await fetch(`${API_URL}/suggestions?${params}`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Erreur:', error);
      setEvents(mockEvents);
    }
    setLoading(false);
  };

  const getFilteredEvents = () => {
    let filtered = events.length > 0 ? events : mockEvents;
    if (contextFilters.length > 0) {
      filtered = filtered.filter(event => 
        contextFilters.some(filter => event.contexte.includes(filter))
      );
    }
    return [...filtered].sort((a, b) => b.score - a.score);
  };

  const handleLocationChange = async () => {
    if (tempLocation.trim()) {
      try {
  const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(tempLocation)}&key=${process.env.REACT_APP_GOOGLE_API_KEY}`;
        const response = await fetch(geocodeUrl);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
          const location = data.results[0].geometry.location;
          const formattedAddress = data.results[0].formatted_address;
          setCurrentCoordinates({ lat: location.lat, lon: location.lng });
          setCurrentLocation(formattedAddress);
          setShowLocationModal(false);
          loadMeteo(location.lat, location.lng);
          if (page === 'results') loadEvents();
        } else {
          alert('Adresse non trouvée');
        }
      } catch (error) {
        console.error('Erreur:', error);
      }
    }
  };

  const handleDateChange = () => {
    if (tempDate.trim()) {
      setCurrentDate(tempDate);
      setShowDateModal(false);
      if (page === 'results') loadEvents();
    }
  };

  useEffect(() => {
    if (page === 'results') loadEvents();
  }, [page, selectedQuickFilter, currentCoordinates, currentDate]);

  const getMeteoIcon = () => {
    if (loadingMeteo) return <Cloud className="w-5 h-5 animate-pulse" />;
    if (meteo.pluie) return <CloudRain className="w-5 h-5" />;
    if (meteo.description.toLowerCase().includes('cloud') || meteo.description.toLowerCase().includes('nuage')) {
      return <Cloud className="w-5 h-5" />;
    }
    return <Sun className="w-5 h-5" />;
  };

  if (page === 'home') {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1499856871958-5b9627545d1a?q=80&w=2020')`,
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-slate-900/70 via-slate-900/60 to-slate-900/80"></div>
        </div>

        <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4 sm:p-6">
          <div className="text-center mb-12 sm:mb-16">
            <h1 className="text-6xl sm:text-8xl font-black text-white mb-3 tracking-tight drop-shadow-2xl">
              THE PLACE<br/>TO GO
            </h1>
            <div className="h-1 w-32 bg-gradient-to-r from-transparent via-white to-transparent mx-auto mb-6"></div>
            <p className="text-xl sm:text-2xl text-white/90 font-light tracking-wide">Votre copilote découverte</p>
          </div>

          {isGeolocating && (
            <div className="mb-6 px-6 py-3 bg-white/95 backdrop-blur-md rounded-full text-slate-800 flex items-center gap-3 shadow-2xl">
              <Navigation className="w-5 h-5 animate-spin text-indigo-600" />
              <span className="font-medium">Localisation en cours...</span>
            </div>
          )}

          {!isGeolocating && hasGeolocated && (
            <div className="mb-6 space-y-3">
              <div className="px-6 py-3 bg-white/95 backdrop-blur-md rounded-full text-slate-800 flex items-center gap-3 shadow-2xl">
                <MapPin className="w-5 h-5 text-indigo-600" />
                <span className="font-medium">{currentLocation}</span>
                <button onClick={handleGeolocate} className="ml-2 text-indigo-600 hover:text-indigo-700 transition-colors" title="Actualiser">
                  <Navigation className="w-4 h-4" />
                </button>
              </div>
              <div className="px-6 py-3 bg-white/95 backdrop-blur-md rounded-full text-slate-800 flex items-center gap-3 justify-center shadow-2xl">
                {getMeteoIcon()}
                <span className="font-medium">
                  {Math.round(meteo.temperature)}°C
                  {meteo.pluie && ' - Il pleut'}
                </span>
              </div>
            </div>
          )}

          <div className="relative mb-12 sm:mb-16">
            {isSearching && (
              <>
                <div className="absolute inset-0 rounded-full bg-white/30 animate-ping" />
                <div className="absolute inset-0 rounded-full bg-white/20 animate-pulse" style={{ animationDelay: '0.3s' }} />
              </>
            )}
            <button 
              onClick={() => handleSearch()} 
              disabled={isSearching} 
              className={`relative w-52 h-52 sm:w-64 sm:h-64 rounded-full bg-white shadow-2xl flex items-center justify-center transform transition-all duration-300 ${isSearching ? 'scale-95' : 'hover:scale-105 active:scale-95'} border-4 border-white/50`}
            >
              <div className="text-center">
                <MapPin className="w-20 h-20 sm:w-24 sm:h-24 text-indigo-600 mx-auto mb-4" />
                <span className="text-2xl sm:text-3xl font-black text-slate-800">
                  {isSearching ? 'Recherche...' : 'GO!'}
                </span>
              </div>
            </button>
          </div>

          <div className="mb-10 max-w-3xl w-full px-2">
            <div className="bg-white/95 backdrop-blur-md px-6 py-4 rounded-2xl mb-6 text-center shadow-2xl">
              <p className="text-slate-800 text-base sm:text-lg font-semibold tracking-wide">Choisissez votre destination</p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4">
              {quickFilters.map((filter) => {
                const Icon = filter.icon;
                return (
                  <button 
                    key={filter.id} 
                    onClick={() => handleSearch(filter.tag)} 
                    className="group flex flex-col items-center justify-center gap-3 px-4 py-6 sm:px-6 sm:py-7 bg-white/95 backdrop-blur-md rounded-2xl transition-all transform hover:scale-105 hover:shadow-2xl shadow-xl font-medium border border-white/50 hover:border-indigo-200"
                  >
                    <Icon className="w-7 h-7 sm:w-8 sm:h-8 text-slate-700 group-hover:text-indigo-600 transition-colors" />
                    <span className="text-slate-800 font-bold text-sm sm:text-base">{filter.label}</span>
                    <span className="text-xs text-slate-500 font-medium">{filter.time}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <button 
            onClick={() => setShowHistory(!showHistory)} 
            className="flex items-center gap-3 px-8 py-4 bg-white/95 backdrop-blur-md rounded-full transition-all shadow-2xl font-semibold text-slate-800 hover:bg-white border border-white/50"
          >
            <History className="w-5 h-5" />
            <span>Historique</span>
          </button>

          {showHistory && (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" onClick={() => setShowHistory(false)}>
              <div className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-3xl font-bold text-slate-800">Historique</h3>
                  <button onClick={() => setShowHistory(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                    <X className="w-7 h-7" />
                  </button>
                </div>
                <p className="text-center text-slate-500 py-12 text-lg">Aucun historique</p>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  const filteredEvents = getFilteredEvents();

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 shadow-xl sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="text-center mb-4">
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              THE PLACE TO GO
            </h1>
          </div>
          
          <div className="flex items-center justify-between mb-5">
            <button 
              onClick={() => { setPage('home'); setSelectedQuickFilter(null); setContextFilters([]); }} 
              className="text-white hover:text-white/80 font-semibold flex items-center gap-2 transition-colors"
            >
              <span className="text-xl">←</span>
              <span>Retour</span>
            </button>
            
            <h2 className="text-2xl font-bold text-white">
              {filteredEvents.length} suggestion{filteredEvents.length > 1 ? 's' : ''}
            </h2>

            <div className="flex gap-2">
              <button 
                onClick={() => setViewMode('list')} 
                className={`p-3 rounded-xl transition-all ${viewMode === 'list' ? 'bg-white/20 text-white' : 'text-white/60 hover:text-white/80'}`}
              >
                <List className="w-5 h-5" />
              </button>
              <button 
                onClick={() => setViewMode('map')} 
                className={`p-3 rounded-xl transition-all ${viewMode === 'map' ? 'bg-white/20 text-white' : 'text-white/60 hover:text-white/80'}`}
              >
                <Map className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3 text-white flex-wrap">
            <button 
              onClick={() => { setTempLocation(currentLocation); setShowLocationModal(true); }} 
              className="flex items-center gap-2 px-5 py-2.5 bg-white/15 hover:bg-white/25 rounded-full backdrop-blur-md transition-all border border-white/20"
            >
              <MapPin className="w-4 h-4" />
              <span className="font-medium text-sm sm:text-base">{currentLocation}</span>
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            
            <button 
              onClick={handleGeolocate} 
              disabled={isGeolocating} 
              className="flex items-center gap-2 px-5 py-2.5 bg-white/15 hover:bg-white/25 rounded-full backdrop-blur-md transition-all border border-white/20"
            >
              <Navigation className={`w-4 h-4 ${isGeolocating ? 'animate-spin' : ''}`} />
              <span className="font-medium text-sm hidden sm:inline">
                {isGeolocating ? 'Localisation...' : 'Me localiser'}
              </span>
            </button>
            
            <button 
              onClick={() => { setTempDate(currentDate); setShowDateModal(true); }} 
              className="flex items-center gap-2 px-5 py-2.5 bg-white/15 hover:bg-white/25 rounded-full backdrop-blur-md transition-all border border-white/20"
            >
              <Calendar className="w-4 h-4" />
              <span className="font-medium text-sm sm:text-base">
                {new Date(currentDate).toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' })}
              </span>
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            
            <div className="flex items-center gap-2 px-5 py-2.5 bg-white/15 rounded-full backdrop-blur-md border border-white/20">
              {getMeteoIcon()}
              <span className="font-medium text-sm sm:text-base">
                {Math.round(meteo.temperature)}°C
              </span>
            </div>
          </div>
        </div>
      </div>

      {viewMode === 'map' ? (
        <div className="h-screen flex flex-col sm:flex-row">
          <div className="flex-1 relative min-h-[50vh] sm:min-h-0">
            <GoogleMapView 
              events={filteredEvents}
              selectedEvent={selectedMapEvent}
              onEventSelect={setSelectedMapEvent}
              onClose={() => setSelectedMapEvent(null)}
              hoveredEventId={hoveredEventId}
              userLocation={currentCoordinates}
              isLoaded={isMapLoaded}
            />
          </div>

          <div className="w-full sm:w-96 bg-white shadow-xl overflow-y-auto max-h-[50vh] sm:max-h-full">
            <div className="p-6 border-b border-slate-200 bg-slate-50">
              <div className="flex items-center gap-2 mb-5">
                <Filter className="w-5 h-5 text-indigo-600" />
                <span className="font-bold text-slate-800 text-lg">Filtrer</span>
              </div>
              
              <div className="flex gap-2 flex-wrap">
                {[
                  { id: 'seul', label: 'Seul', icon: User }, 
                  { id: 'couple', label: 'Couple', icon: Heart }, 
                  { id: 'groupe', label: 'Groupe', icon: Users }, 
                  { id: 'famille', label: 'Famille', icon: Users }
                ].map(({ id, label, icon: Icon }) => (
                  <button 
                    key={id} 
                    onClick={() => toggleContextFilter(id)} 
                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                      contextFilters.includes(id) 
                        ? 'bg-indigo-600 text-white shadow-lg' 
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="p-4 space-y-3">
              {selectedMapEvent ? (
                <div className="bg-slate-50 rounded-2xl p-6 border-2 border-indigo-200">
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="font-bold text-xl text-slate-800">{selectedMapEvent.nom}</h3>
                    <button 
                      onClick={() => setSelectedMapEvent(null)} 
                      className="text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>
                  
                  <p className="text-sm text-slate-600 mb-4">{selectedMapEvent.description}</p>

                  <div className="space-y-2 mb-5">
                    <div className="flex items-center gap-2 text-sm">
                      <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                      <span className="font-semibold">{selectedMapEvent.qualite}/5</span>
                      <span className="text-slate-500">({selectedMapEvent.nbAvis})</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-indigo-600" />
                      <span>{selectedMapEvent.horaire} - {selectedMapEvent.heureFermeture}</span>
                    </div>
                    <div className="text-sm font-bold text-indigo-600">{selectedMapEvent.prix}</div>
                    {selectedMapEvent.pmr && (
                      <div className="flex items-center gap-2 text-sm">
                        <Accessibility className="w-4 h-4 text-blue-600" />
                        <span className="font-semibold text-blue-600">Accessible PMR</span>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <a 
                      href={`https://www.google.com/maps/dir/?api=1&destination=${selectedMapEvent.latitude},${selectedMapEvent.longitude}`} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-xl font-semibold text-sm hover:shadow-lg transition-all"
                    >
                      <Navigation className="w-4 h-4" />
                      <span>Y ALLER</span>
                    </a>
                    {selectedMapEvent.urlSite && (
                      <a 
                        href={selectedMapEvent.urlSite} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-white border-2 border-slate-200 text-slate-700 rounded-xl font-semibold text-sm hover:border-slate-300 transition-all"
                      >
                        <Globe className="w-4 h-4" />
                        <span>Site web</span>
                      </a>
                    )}
                    {selectedMapEvent.urlAvisGoogle && (
                      <a 
                        href={selectedMapEvent.urlAvisGoogle} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-white border-2 border-yellow-200 text-yellow-600 rounded-xl font-semibold text-sm hover:border-yellow-300 transition-all"
                      >
                        <Star className="w-4 h-4" />
                        <span>Avis</span>
                      </a>
                    )}
                  </div>
                </div>
              ) : (
                filteredEvents.map((event) => (
                  <div 
                    key={event.id} 
                    onClick={() => setSelectedMapEvent(event)} 
                    onMouseEnter={() => setHoveredEventId(event.id)} 
                    onMouseLeave={() => setHoveredEventId(null)} 
                    className="bg-white rounded-2xl p-5 shadow hover:shadow-lg transition-all cursor-pointer border border-slate-200 hover:border-indigo-300"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-bold text-slate-800">{event.nom}</h4>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">{event.description}</p>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Clock className="w-3 h-3" />
                      <span>{event.horaire}</span>
                      <span>•</span>
                      <span className="font-semibold text-indigo-600">{event.prix}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto px-3 sm:px-4 py-6 sm:py-8">
          <div className="bg-white rounded-2xl p-5 sm:p-6 mb-5 sm:mb-6 shadow-md border border-slate-200">
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-5 h-5 text-indigo-600" />
              <span className="font-bold text-slate-800 text-base sm:text-lg">Filtrer par contexte</span>
            </div>
            
            <div className="flex gap-2 sm:gap-3 flex-wrap">
              {[
                { id: 'seul', label: 'Seul', icon: User }, 
                { id: 'couple', label: 'En couple', icon: Heart }, 
                { id: 'groupe', label: 'En groupe', icon: Users }, 
                { id: 'famille', label: 'En famille', icon: Users }
              ].map(({ id, label, icon: Icon }) => (
                <button 
                  key={id} 
                  onClick={() => toggleContextFilter(id)} 
                  className={`flex items-center gap-2 px-4 py-2.5 sm:px-6 sm:py-3 rounded-full transition-all font-semibold text-xs sm:text-base ${
                    contextFilters.includes(id) 
                      ? 'bg-indigo-600 text-white shadow-lg' 
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5">
            {loading && (
              <div className="col-span-full bg-white rounded-2xl p-16 shadow-md text-center border border-slate-200">
                <div className="animate-spin w-14 h-14 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-5"></div>
                <p className="text-slate-600 font-medium">Chargement...</p>
              </div>
            )}

            {!loading && filteredEvents.length === 0 && (
              <div className="col-span-full bg-white rounded-2xl p-16 shadow-md text-center border border-slate-200">
                <p className="text-slate-500 text-lg font-medium">Aucune activité ne correspond</p>
              </div>
            )}

            {!loading && filteredEvents.map((event, index) => (
              <div 
                key={event.id} 
                className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all overflow-hidden border border-slate-200 hover:border-indigo-300"
              >
                {event.imageUrl && (
                  <div className="relative h-48 overflow-hidden">
                    <img 
                      src={event.imageUrl} 
                      alt={event.nom}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3 bg-white rounded-full w-8 h-8 flex items-center justify-center shadow-lg">
                      <span className="text-xs font-bold text-indigo-600">#{index + 1}</span>
                    </div>
                    <div className="absolute top-3 right-3 bg-gradient-to-br from-indigo-600 to-indigo-800 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
                      {event.categorie}
                    </div>
                  </div>
                )}

                <div className="p-5">
                  <a 
                    href={event.urlSite} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block mb-3"
                  >
                    <h3 className="font-bold text-xl text-slate-800 hover:text-indigo-600 transition-colors hover:underline">
                      {event.nom}
                    </h3>
                  </a>
                  
                  <a 
                    href={event.urlAvisGoogle} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 mb-3 hover:opacity-80 transition-opacity"
                  >
                    {Array.from({ length: Math.floor(event.qualite) }, (_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    ))}
                    <span className="text-sm text-slate-600 ml-1 font-medium">({event.nbAvis} avis)</span>
                  </a>
                  
                  <p className="text-sm text-slate-600 mb-4 line-clamp-2 leading-relaxed">
                    {event.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    <div className="flex items-center gap-2 bg-indigo-50 px-3 py-2 rounded-xl border border-indigo-200">
                      <Clock className="w-4 h-4 text-indigo-600" />
                      <span className="text-sm font-semibold text-slate-700">{event.horaire}</span>
                    </div>
                    
                    <a
                      href={`https://www.google.com/maps/dir/?api=1&destination=${event.latitude},${event.longitude}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-xl border border-blue-200 hover:bg-blue-100 transition-colors"
                    >
                      <MapPin className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-semibold text-slate-700">{event.distance} km</span>
                      <span className="text-xs text-slate-500">• {Math.round(event.distance * 15)} min</span>
                    </a>
                    
                    <div className="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200">
                      <span className="text-sm font-bold text-emerald-700">{event.prix}</span>
                    </div>
                    
                    {event.pmr && (
                      <div className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-xl border border-blue-200">
                        <Accessibility className="w-4 h-4 text-blue-600" />
                        <span className="text-xs font-semibold text-blue-700">PMR</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showLocationModal && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" 
          onClick={() => setShowLocationModal(false)}
        >
          <div 
            className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl" 
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-slate-800">Changer de lieu</h3>
              <button 
                onClick={() => setShowLocationModal(false)} 
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <input 
              type="text" 
              value={tempLocation} 
              onChange={(e) => setTempLocation(e.target.value)} 
              placeholder="Entrez une adresse" 
              className="w-full px-5 py-3 border-2 border-slate-200 rounded-xl focus:border-indigo-500 focus:outline-none mb-5 text-slate-800"
            />
            <button 
              onClick={handleLocationChange} 
              className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 text-white py-3.5 rounded-xl font-bold hover:shadow-lg transition-all"
            >
              Valider
            </button>
          </div>
        </div>
      )}

      {showDateModal && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" 
          onClick={() => setShowDateModal(false)}
        >
          <div 
            className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl" 
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-slate-800">Changer de date</h3>
              <button 
                onClick={() => setShowDateModal(false)} 
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <input 
              type="date" 
              value={tempDate} 
              onChange={(e) => setTempDate(e.target.value)} 
              className="w-full px-5 py-3 border-2 border-slate-200 rounded-xl focus:border-indigo-500 focus:outline-none mb-5 text-slate-800"
            />
            <button 
              onClick={handleDateChange} 
              className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 text-white py-3.5 rounded-xl font-bold hover:shadow-lg transition-all"
            >
              Valider
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;