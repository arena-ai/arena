/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__models__Message } from '../models/app__models__Message';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class UtilsService {

    /**
     * Test Email
     * Test emails.
     * @returns app__models__Message Successful Response
     * @throws ApiError
     */
    public static testEmail({
        emailTo,
    }: {
        emailTo: string,
    }): CancelablePromise<app__models__Message> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/utils/test-email/',
            query: {
                'email_to': emailTo,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
