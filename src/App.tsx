import React, { useState, useEffect } from 'react';
import { Bot, Zap, Shield, Cpu, MessageCircle, Star, ChevronRight, ExternalLink, X } from 'lucide-react';

function App() {
  const [isVisible, setIsVisible] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleTelegramClick = () => {
    window.open('https://t.me/gptcassiel9_bot', '_blank');
  };

  const features = [
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Молниеносная скорость",
      description: "Мгновенные ответы на базе передовых AI технологий"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Безопасность",
      description: "Ваши разговоры зашифрованы и защищены"
    },
    {
      icon: <Cpu className="w-8 h-8" />,
      title: "Нейросеть",
      description: "Продвинутые алгоритмы машинного обучения"
    },
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Умный чат",
      description: "Контекстные разговоры, которые кажутся естественными"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white relative overflow-hidden">
      {/* Анимированный фон */}
      <div className="absolute inset-0 opacity-20">
        <div 
          className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-green-500/10"
          style={{
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)`
          }}
        />
        <div className="absolute inset-0">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-cyan-400 rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${2 + Math.random() * 3}s`
              }}
            />
          ))}
        </div>
      </div>

      {/* Сетка */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.1)_1px,transparent_1px)] bg-[length:50px_50px]" />
      </div>

      {/* Заголовок */}
      <header className="relative z-10 px-6 py-8">
        <nav className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Bot className="w-10 h-10 text-cyan-400" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Cassiel9GPT
            </div>
          </div>
          <div className="flex items-center space-x-6">
            <a href="#features" className="text-gray-300 hover:text-cyan-400 transition-colors">Возможности</a>
            <a href="#about" className="text-gray-300 hover:text-cyan-400 transition-colors">О боте</a>
            <button 
              onClick={handleTelegramClick}
              className="bg-gradient-to-r from-cyan-500 to-purple-500 px-6 py-2 rounded-full text-white font-semibold hover:shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 transform hover:scale-105"
            >
              Запустить бота
            </button>
          </div>
        </nav>
      </header>

      {/* Главная секция */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="inline-block mb-6">
              <div className="relative">
                <div className="w-32 h-32 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-cyan-500/50">
                  <Bot className="w-16 h-16 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                  <Zap className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-cyan-400 via-purple-400 to-green-400 bg-clip-text text-transparent">
              Cassiel9GPT
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Ваш продвинутый AI-компаньон в Telegram. Испытайте будущее разговорного ИИ с 
              <span className="text-cyan-400 font-semibold"> нейронным интеллектом</span> и 
              <span className="text-purple-400 font-semibold"> кибернетической точностью</span>.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button 
                onClick={handleTelegramClick}
                className="group bg-gradient-to-r from-cyan-500 to-purple-500 px-8 py-4 rounded-full text-white font-bold text-lg hover:shadow-2xl hover:shadow-cyan-500/50 transition-all duration-300 transform hover:scale-105 flex items-center space-x-2"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Начать общение</span>
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              
              {/* <button 
                onClick={handleTelegramClick}
                className="group border-2 border-cyan-400 px-8 py-4 rounded-full text-cyan-400 font-bold text-lg hover:bg-cyan-400/10 hover:shadow-lg hover:shadow-cyan-400/25 transition-all duration-300 flex items-center space-x-2"
              >
                <ExternalLink className="w-5 h-5" />
                <span>Посмотреть демо</span>
              </button> */}
            </div>
          </div>
        </div>
      </section>

      {/* Секция возможностей */}
      <section id="features" className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Нейронные возможности
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Работает на передовых AI технологиях и создан для будущего
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className={`group bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 hover:border-cyan-400/50 hover:shadow-xl hover:shadow-cyan-500/10 transition-all duration-500 transform hover:scale-105 ${
                  isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
                }`}
                style={{ transitionDelay: `${index * 100}ms` }}
              >
                <div className="text-cyan-400 mb-4 group-hover:scale-110 transition-transform duration-300">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-3 text-white group-hover:text-cyan-400 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* О боте */}
      <section id="about" className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-gray-800/50 to-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-3xl p-12 md:p-16">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  О Cassiel9GPT
                </h2>
                <p className="text-xl text-gray-300 mb-6 leading-relaxed">
                  Рожденный из слияния передовых нейронных сетей и кибернетического интеллекта, 
                  Cassiel9GPT представляет следующую эволюцию разговорного ИИ.
                </p>
                <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                  Наш бот использует самые современные языковые модели для предоставления умных, 
                  контекстно-зависимых ответов, которые кажутся естественными и человечными. 
                  Нужна ли вам помощь, хотите ли вы обсудить идеи или просто поболтать, 
                  Cassiel9GPT - ваш цифровой компаньон в киберпространстве.
                </p>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Star className="w-5 h-5 text-yellow-400" />
                    <span className="text-white font-semibold">AI-Powered</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-green-400" />
                    <span className="text-white font-semibold">Безопасный</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Zap className="w-5 h-5 text-cyan-400" />
                    <span className="text-white font-semibold">Быстрый</span>
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="w-full h-80 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-2xl flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-[linear-gradient(45deg,rgba(0,255,255,0.1)_1px,transparent_1px),linear-gradient(-45deg,rgba(128,0,128,0.1)_1px,transparent_1px)] bg-[length:20px_20px]" />
                  <Bot className="w-32 h-32 text-cyan-400 relative z-10" />
                  <div className="absolute top-4 right-4 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <div className="absolute bottom-4 left-4 w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                  <div className="absolute top-1/2 left-4 w-1 h-1 bg-cyan-400 rounded-full animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Призыв к действию */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-cyan-500/10 to-purple-500/10 backdrop-blur-sm border border-cyan-400/30 rounded-3xl p-12 md:p-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Готовы войти в будущее?
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Присоединяйтесь к тысячам пользователей, которые уже открыли для себя силу Cassiel9GPT. 
              Ваш кибернетический компаньон ждет вас в Telegram.
            </p>
            <button 
              onClick={handleTelegramClick}
              className="group bg-gradient-to-r from-cyan-500 to-purple-500 px-12 py-6 rounded-full text-white font-bold text-xl hover:shadow-2xl hover:shadow-cyan-500/50 transition-all duration-300 transform hover:scale-105 flex items-center space-x-3 mx-auto"
            >
              <MessageCircle className="w-6 h-6" />
              <span>Запустить Cassiel9GPT</span>
              <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </section>

      {/* Подвал */}
      <footer className="relative z-10 px-6 py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <Bot className="w-8 h-8 text-cyan-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Cassiel9GPT
            </span>
          </div>
          <p className="text-gray-400 mb-4">
            Будущее AI-разговоров уже здесь
          </p>
          <div className="flex items-center justify-center space-x-6">
            <button 
              onClick={() => setShowPrivacyModal(true)}
              className="text-gray-400 hover:text-cyan-400 transition-colors cursor-pointer"
            >
              Политика конфиденциальности
            </button>
            {/* <a href="#" className="text-gray-400 hover:text-cyan-400 transition-colors">
              Условия использования
            </a>
            <a href="#" className="text-gray-400 hover:text-cyan-400 transition-colors">
              Контакты
            </a> */}
          </div>
        </div>
      </footer>

      {/* Модальное окно политики конфиденциальности */}
      {showPrivacyModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-cyan-400/30 rounded-2xl max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="sticky top-0 bg-gray-900 border-b border-gray-700 p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Политика конфиденциальности
              </h2>
              <button 
                onClick={() => setShowPrivacyModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6 text-gray-300">
              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">1. Сбор информации</h3>
                <p className="leading-relaxed">
                  Cassiel9GPT собирает только необходимую информацию для предоставления качественного сервиса. 
                  Мы обрабатываем ваши сообщения исключительно для генерации ответов и улучшения работы бота.
                </p>
              </section>

              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">2. Использование данных</h3>
                <p className="leading-relaxed">
                  Ваши данные используются только для:
                </p>
                <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                  <li>Предоставления ответов на ваши запросы</li>
                  <li>Улучшения качества работы AI-модели</li>
                  <li>Обеспечения безопасности сервиса</li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">3. Защита данных</h3>
                <p className="leading-relaxed">
                  Мы применяем современные методы шифрования и защиты данных. Ваши разговоры защищены 
                  end-to-end шифрованием и не передаются третьим лицам без вашего согласия.
                </p>
              </section>

              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">4. Хранение данных</h3>
                <p className="leading-relaxed">
                  Сообщения хранятся в зашифрованном виде в течение ограниченного времени, необходимого 
                  для поддержания контекста разговора. Старые сообщения автоматически удаляются.
                </p>
              </section>

              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">5. Ваши права</h3>
                <p className="leading-relaxed">
                  Вы имеете право:
                </p>
                <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                  <li>Запросить удаление ваших данных</li>
                  <li>Получить копию ваших данных</li>
                  <li>Ограничить обработку ваших данных</li>
                  <li>Отозвать согласие на обработку</li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">6. Контакты</h3>
                <p className="leading-relaxed">
                  По вопросам конфиденциальности обращайтесь к нам через бота 
                  <span className="text-cyan-400 font-semibold"> @gptcassiel9_bot</span> или 
                  отправьте сообщение с темой "Конфиденциальность".
                </p>
              </section>

              <section>
                <h3 className="text-xl font-semibold text-cyan-400 mb-3">7. Изменения политики</h3>
                <p className="leading-relaxed">
                  Мы можем обновлять эту политику конфиденциальности. О существенных изменениях 
                  мы уведомим вас через бота или на этом сайте.
                </p>
              </section>

              <div className="pt-4 border-t border-gray-700">
                <p className="text-sm text-gray-400">
                  Последнее обновление: {new Date().toLocaleDateString('ru-RU')}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;