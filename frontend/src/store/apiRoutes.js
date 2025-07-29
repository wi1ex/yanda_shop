// src/store/apiRoutes.js
export const API = {
  general: {
    healthCheck:        '/api/general',                      // GET    - health check
    saveUser:           '/api/general/save_user',            // POST   - сохранить/обновить Telegram-пользователя
    getUserProfile:     '/api/general/get_user_profile',     // GET    - получить профиль
    getParameters:      '/api/general/get_parameters',       // GET    - получить публичные настройки
    listReviews:        '/api/general/list_reviews',         // GET    - получить список отзывов
    createRequest:      '/api/general/create_request',       // POST   - отправить заявку на поиск товара
  },
  product: {
    listProducts:       '/api/product/list_products',        // GET    - список товаров
    getProduct:         '/api/product/get_product',          // GET    - детали одного товара
    getCart:            '/api/product/get_cart',             // GET    - получить корзину пользователя
    saveCart:           '/api/product/save_cart',            // POST   - сохранить корзину
    getFavorites:       '/api/product/get_favorites',        // GET    - получить избранное
    saveFavorites:      '/api/product/save_favorites',       // POST   - сохранить избранное
  },
  admin: {
    setUserRole:        '/api/admin/set_user_role',          // GET    - установить пользователю роль
    getDailyVisits:     '/api/admin/get_daily_visits',       // GET    - статистика визитов по часам
    getLogs:            '/api/admin/get_logs',               // GET    - журнал
    getSheetUrls:       '/api/admin/get_sheet_urls',         // GET    - URL Google Sheets
    updateSheetUrl:     '/api/admin/update_sheet_url',       // POST   - сохранить URL таблицы
    importSheet:        '/api/admin/import_sheet',           // POST   - импорт CSV из Sheets
    previewSheet:       '/api/admin/preview_sheet',          // POST   - проверка CSV из Sheets
    uploadImages:       '/api/admin/upload_images',          // POST   - загрузка ZIP с изображениями
    previewImages:      '/api/admin/preview_images',         // POST   - проверка ZIP с изображениями
    getSettings:        '/api/admin/get_settings',           // GET    - получить список настроек
    updateSetting:      '/api/admin/update_setting',         // POST   - изменить список настроек
    deleteSetting:      '/api/admin/delete_setting',         // DELETE - удалить параметр настроек
    createReview:       '/api/admin/create_review',          // POST   - загрузить новый отзыв
    deleteReview:       '/api/admin/delete_review',          // DELETE - удалить отзыв
    listRequests:       '/api/admin/list_requests',          // GET    - получить список заявок на поиск товара
    deleteRequest:      '/api/admin/delete_request',         // DELETE - удалить заявку на поиск товара
    listUsers:          '/api/admin/list_users',             // GET    - получить список пользователей
  }
}
