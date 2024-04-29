/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $EventAttributeCreate = {
    properties: {
        event_id: {
            type: 'number',
            isRequired: true,
        },
        attribute_id: {
            type: 'number',
            isRequired: true,
        },
        value: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
