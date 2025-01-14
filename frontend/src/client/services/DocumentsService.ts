/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__models__Message } from '../models/app__models__Message';
import type { Body_documents_create_file } from '../models/Body_documents_create_file';
import type { Document } from '../models/Document';
import type { Documents } from '../models/Documents';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DocumentsService {

    /**
     * Read Files
     * @returns Documents Successful Response
     * @throws ApiError
     */
    public static readFiles(): CancelablePromise<Documents> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/documents/',
        });
    }

    /**
     * Create File
     * @returns Document Successful Response
     * @throws ApiError
     */
    public static createFile({
        formData,
    }: {
        formData: Body_documents_create_file,
    }): CancelablePromise<Document> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/documents/',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read File
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readFile({
        name,
    }: {
        name: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/documents/{name}',
            path: {
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete File
     * Delete a file.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static deleteFile({
        name,
    }: {
        name: string,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/documents/{name}',
            path: {
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read File As Text
     * @returns string Successful Response
     * @throws ApiError
     */
    public static readFileAsText({
        name,
        startPage,
        endPage,
    }: {
        name: string,
        startPage?: number,
        endPage?: (number | null),
    }): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/documents/{name}/as_text',
            path: {
                'name': name,
            },
            query: {
                'start_page': startPage,
                'end_page': endPage,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read File As Png
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readFileAsPng({
        name,
        startPage,
        endPage,
    }: {
        name: string,
        startPage?: number,
        endPage?: (number | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/documents/{name}/as_png',
            path: {
                'name': name,
            },
            query: {
                'start_page': startPage,
                'end_page': endPage,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
