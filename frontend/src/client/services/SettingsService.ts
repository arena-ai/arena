/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SettingCreate } from '../models/SettingCreate';
import type { SettingOut } from '../models/SettingOut';
import type { SettingsOut } from '../models/SettingsOut';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class SettingsService {

    /**
     * Read Settings
     * Retrieve Settings.
     * @returns SettingsOut Successful Response
     * @throws ApiError
     */
    public static readSettings({
        skip,
        limit = 100,
    }: {
        skip?: number,
        limit?: number,
    }): CancelablePromise<SettingsOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/settings/',
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
     * Create Setting
     * Create new setting.
     * @returns SettingOut Successful Response
     * @throws ApiError
     */
    public static createSetting({
        requestBody,
    }: {
        requestBody: SettingCreate,
    }): CancelablePromise<SettingOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/settings/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Setting
     * Get setting by name.
     * @returns SettingOut Successful Response
     * @throws ApiError
     */
    public static readSetting({
        name,
    }: {
        name: string,
    }): CancelablePromise<SettingOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/settings/{name}',
            path: {
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Setting Get
     * Create new setting.
     * @returns SettingOut Successful Response
     * @throws ApiError
     */
    public static createSettingGet({
        name,
        content,
    }: {
        name: string,
        content: string,
    }): CancelablePromise<SettingOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/settings/{name}/{content}',
            path: {
                'name': name,
                'content': content,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
