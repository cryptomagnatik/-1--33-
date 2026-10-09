<?php

declare(strict_types=1);

namespace App;

use RuntimeException;

// клас читає дані з файлу
class BookRepository
{
    public function __construct(private string $filePath)
    {
    }

    public function all(): array
    {
        $json = @file_get_contents($this->filePath);
        if ($json === false) {
            throw new RuntimeException('Не вдалося прочитати файл книг.');
        }

        $books = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        if (!is_array($books) || !array_is_list($books)) {
            throw new RuntimeException('Файл має містити JSON-масив книг.');
        }

        $ids = [];
        foreach ($books as $book) {
            if (!is_array($book)
                || !isset($book['id'], $book['title'], $book['author'], $book['year'], $book['genre'])
                || !is_int($book['id']) || $book['id'] < 1
                || !is_int($book['year'])
                || !is_string($book['title']) || !is_string($book['author'])
                || !is_string($book['genre']) || trim($book['genre']) === ''
                || in_array($book['id'], $ids, true)) {
                throw new RuntimeException('Некоректний запис книги у файлі.');
            }
            $ids[] = $book['id'];
        }

        return $books;
    }
}
