export const API = {
  general: {
    healthCheck:              '/api/general',                           // GET    - health check
    saveUser:                 '/api/general/save_user',                 // POST   - сохранить/обновить TG-пользователя
    getUserProfile:           '/api/general/get_user_profile',          // GET    - получить данные профиля
    updateProfile:            '/api/general/update_profile',            // PUT    - обновить данные профиля
    getParameters:            '/api/general/get_parameters',            // GET    - получить публичные настройки
    listReviews:              '/api/general/list_reviews',              // GET    - получить список отзывов
    createRequest:            '/api/general/create_request',            // POST   - отправить заявку на поиск товара
    getUserOrders:            '/api/general/get_user_orders',           // GET    - получить список заказов
    getUserOrder:             '/api/general/get_user_order',            // GET    - получить детали заказа
    listAddresses:            '/api/general/list_addresses',            // GET    - получить список адресов
    createAddress:            '/api/general/add_address',               // POST   - добавить адрес
    updateAddress:            '/api/general/update_address',            // PUT    - обновить данные дареса
    deleteAddress:            '/api/general/delete_address',            // DELETE - удалить адрес
  },
  product: {
    listProducts:             '/api/product/list_products',             // GET    - список товаров
    getProduct:               '/api/product/get_product',               // GET    - детали одного товара
    getCart:                  '/api/product/get_cart',                  // GET    - получить корзину пользователя
    saveCart:                 '/api/product/save_cart',                 // POST   - сохранить корзину
    getFavorites:             '/api/product/get_favorites',             // GET    - получить избранное
    saveFavorites:            '/api/product/save_favorites',            // POST   - сохранить избранное
  },
  auth: {
    requestRegistrationCode:  '/api/auth/request_registration_code',    // POST   - Регистрация: запрос кода
    verifyRegistrationCode:   '/api/auth/verify_registration_code',     // POST   - Регистрация: верификация кода
    requestLoginCode:         '/api/auth/request_login_code',           // POST   - Авторизация: запрос кода
    verifyLoginCode:          '/api/auth/verify_login_code',            // POST   - Авторизация: верификация кода
  },
  admin: {
    setUserRole:              '/api/admin/set_user_role',               // GET    - установить пользователю роль
    getDailyVisits:           '/api/admin/get_daily_visits',            // GET    - статистика визитов по часам
    getLogs:                  '/api/admin/get_logs',                    // GET    - журнал
    syncAll:                  '/api/admin/sync_all',                    // POST   - проверка и загрузка Sheets и ZIP
    getSettings:              '/api/admin/get_settings',                // GET    - получить список настроек
    updateSetting:            '/api/admin/update_setting',              // POST   - изменить список настроек
    deleteSetting:            '/api/admin/delete_setting',              // DELETE - удалить параметр настроек
    createReview:             '/api/admin/create_review',               // POST   - загрузить новый отзыв
    deleteReview:             '/api/admin/delete_review',               // DELETE - удалить отзыв
    listRequests:             '/api/admin/list_requests',               // GET    - получить список заявок на поиск товара
    deleteRequest:            '/api/admin/delete_request',              // DELETE - удалить заявку на поиск товара
    listUsers:                '/api/admin/list_users',                  // GET    - получить список пользователей
  }
}
