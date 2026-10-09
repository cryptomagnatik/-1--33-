<?php

declare(strict_types=1);

use App\BookRepository;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;

// Composer завантажує бібліотеку Symfony та клас BookRepository.
require dirname(__DIR__) . '/vendor/autoload.php';

function respond(array $body, int $status = 200, array $headers = []): never
{
    $response = new JsonResponse(null, $status, $headers);
    $response->setEncodingOptions(JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    $response->setData($body);
    $response->send();
    exit;
}

try {
    $request = Request::createFromGlobals();
    if ($request->getMethod() !== 'GET') {
        respond(['error' => 'Дозволено лише метод GET.'], 405, ['Allow' => 'GET']);
    }

    $params = $request->query->all();
    foreach ($params as $key => $value) {
        if (!in_array($key, ['id', 'genre', 'action'], true) || !is_string($value)) {
            respond(['error' => 'Невідомий параметр або некоректний формат.'], 400);
        }
    }
    if (count($params) > 1) {
        respond(['error' => 'Передайте лише один параметр: id, genre або action.'], 400);
    }
    if (isset($params['action']) && $params['action'] !== 'genres') {
        respond(['error' => 'Єдина доступна дія: action=genres.'], 400);
    }
    if (isset($params['id'])
        && filter_var($params['id'], FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]) === false) {
        respond(['error' => 'ID має бути цілим додатним числом.'], 400);
    }
    if (isset($params['genre']) && trim($params['genre']) === '') {
        respond(['error' => 'Жанр не може бути порожнім.'], 400);
    }

    $repository = new BookRepository(dirname(__DIR__) . '/data/books.json');
    $books = $repository->all();

    if (isset($params['action'])) {
        $genres = array_values(array_unique(array_column($books, 'genre')));
        respond(['count' => count($genres), 'data' => $genres]);
    }

    if (isset($params['id'])) {
        foreach ($books as $book) {
            if ($book['id'] === (int) $params['id']) {
                respond(['data' => $book]);
            }
        }
        respond(['error' => 'Книгу з таким ID не знайдено.'], 404);
    }

    if (isset($params['genre'])) {
        $genre = trim($params['genre']);
        $books = array_values(array_filter($books, fn(array $book): bool => $book['genre'] === $genre));
    }

    respond(['count' => count($books), 'data' => $books]);
} catch (Throwable $exception) {
    error_log($exception->getMessage());
    respond(['error' => 'Помилка читання даних на сервері. Перевірте файл books.json.'], 500);
}
