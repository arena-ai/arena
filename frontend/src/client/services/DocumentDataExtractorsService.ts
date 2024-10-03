/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__models__Message } from '../models/app__models__Message';
import type { Body_document_data_extractors_extract_from_file } from '../models/Body_document_data_extractors_extract_from_file';
import type { DocumentDataExampleCreate } from '../models/DocumentDataExampleCreate';
import type { DocumentDataExampleOut } from '../models/DocumentDataExampleOut';
import type { DocumentDataExampleUpdate } from '../models/DocumentDataExampleUpdate';
import type { DocumentDataExtractorCreate } from '../models/DocumentDataExtractorCreate';
import type { DocumentDataExtractorOut } from '../models/DocumentDataExtractorOut';
import type { DocumentDataExtractorsOut } from '../models/DocumentDataExtractorsOut';
import type { DocumentDataExtractorUpdate } from '../models/DocumentDataExtractorUpdate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DocumentDataExtractorsService {

    /**
     * Read Document Data Extractors
     * Retrieve DocumentDataExtractors.
     * @returns DocumentDataExtractorsOut Successful Response
     * @throws ApiError
     */
    public static readDocumentDataExtractors({
        skip,
        limit = 100,
    }: {
        skip?: number,
        limit?: number,
    }): CancelablePromise<DocumentDataExtractorsOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dde/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Document Data Extractor
     * Create a new DocumentDataExtractor.
     * @returns DocumentDataExtractorOut Successful Response
     * @throws ApiError
     */
    public static createDocumentDataExtractor({
        requestBody,
    }: {
        requestBody: DocumentDataExtractorCreate,
    }): CancelablePromise<DocumentDataExtractorOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dde/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Document Data Extractor
     * Get a DocumentDataExtractor by ID.
     * @returns DocumentDataExtractorOut Successful Response
     * @throws ApiError
     */
    public static readDocumentDataExtractor({
        id,
    }: {
        id: number,
    }): CancelablePromise<DocumentDataExtractorOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dde/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Document Data Extractor
     * Update a DocumentDataExtractor.
     * @returns DocumentDataExtractorOut Successful Response
     * @throws ApiError
     */
    public static updateDocumentDataExtractor({
        id,
        requestBody,
    }: {
        id: number,
        requestBody: DocumentDataExtractorUpdate,
    }): CancelablePromise<DocumentDataExtractorOut> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/dde/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Document Data Extractor
     * Delete a DocumentDataExtractor.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static deleteDocumentDataExtractor({
        id,
    }: {
        id: number,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/dde/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Document Data Extractor By Name
     * Get DocumentDataExtractor by name.
     * @returns DocumentDataExtractorOut Successful Response
     * @throws ApiError
     */
    public static readDocumentDataExtractorByName({
        name,
    }: {
        name: string,
    }): CancelablePromise<DocumentDataExtractorOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dde/name/{name}',
            path: {
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Document Data Example
     * Create new DocumentDataExample.
     * @returns DocumentDataExampleOut Successful Response
     * @throws ApiError
     */
    public static createDocumentDataExample({
        name,
        requestBody,
    }: {
        name: string,
        requestBody: DocumentDataExampleCreate,
    }): CancelablePromise<DocumentDataExampleOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dde/{name}/example',
            path: {
                'name': name,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Document Data Example
     * Create new DocumentDataExample.
     * @returns DocumentDataExampleOut Successful Response
     * @throws ApiError
     */
    public static updateDocumentDataExample({
        name,
        id,
        requestBody,
    }: {
        name: string,
        id: number,
        requestBody: DocumentDataExampleUpdate,
    }): CancelablePromise<DocumentDataExampleOut> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/dde/{name}/example/{id}',
            path: {
                'name': name,
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Document Data Example
     * Delete an event identifier.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static deleteDocumentDataExample({
        name,
        id,
    }: {
        name: string,
        id: number,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/dde/{name}/example/{id}',
            path: {
                'name': name,
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Extract From File
     * @returns any Successful Response
     * @throws ApiError
     */
    public static extractFromFile({
        name,
        formData,
    }: {
        name: string,
        formData: Body_document_data_extractors_extract_from_file,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dde/extract/{name}',
            path: {
                'name': name,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
