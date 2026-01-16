<?php

/**
 * UserSettingLayoutRestController - REST API for layout-based custom user settings.
 *
 * This controller provides API endpoints for managing custom user settings that are
 * defined via the Admin > Layouts system using the 'USR' form type.
 *
 * @package   OpenEMR
 * @link      https://plhi.lab.indianapolis.iu.edu
 * @author    Saptarshi Purkayastha
 * @copyright Copyright (c) 2025 PLHI
 * @license   https://github.com/iupui-soic/openemr/blob/master/LICENSE GNU General Public License 3
 */

namespace OpenEMR\RestControllers;

use Nyholm\Psr7\Response;
use OpenEMR\Common\Http\HttpRestRequest;
use OpenEMR\Services\UserSettings\UserSettingLayoutService;
use OpenEMR\Validators\ProcessingResult;

class UserSettingLayoutRestController
{
    private UserSettingLayoutService $service;

    public function __construct()
    {
        $this->service = new UserSettingLayoutService();
    }

    /**
     * Get all custom user settings for the current user.
     *
     * @param HttpRestRequest $request The HTTP request object
     * @return Response
     */
    public function getAll(HttpRestRequest $request): Response
    {
        $userId = $request->getRequestUserId();
        $processingResult = $this->service->getAllUserSettingsForApi($userId);
        return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 200, true);
    }

    /**
     * Get a specific custom user setting by field_id.
     *
     * @param string $fieldId The field identifier
     * @param HttpRestRequest $request The HTTP request object
     * @return Response
     */
    public function getOne(string $fieldId, HttpRestRequest $request): Response
    {
        $userId = $request->getRequestUserId();
        $processingResult = $this->service->getUserSettingWithDefinition($userId, $fieldId);

        if ($processingResult->hasErrors() || count($processingResult->getData()) == 0) {
            return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 404);
        }

        return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 200);
    }

    /**
     * Update a custom user setting.
     *
     * @param string $fieldId The field identifier
     * @param array $data The data containing field_value
     * @param HttpRestRequest $request The HTTP request object
     * @return Response
     */
    public function put(string $fieldId, array $data, HttpRestRequest $request): Response
    {
        $userId = $request->getRequestUserId();
        $value = $data['field_value'] ?? null;

        $processingResult = $this->service->setUserSettingValue($userId, $fieldId, $value);

        if ($processingResult->hasErrors()) {
            return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 400);
        }

        return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 200);
    }

    /**
     * Delete (reset) a custom user setting to its default value.
     *
     * @param string $fieldId The field identifier
     * @param HttpRestRequest $request The HTTP request object
     * @return Response
     */
    public function delete(string $fieldId, HttpRestRequest $request): Response
    {
        $userId = $request->getRequestUserId();
        $processingResult = $this->service->deleteUserSettingValue($userId, $fieldId);
        return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 200);
    }

    /**
     * Get all available USR layout fields (field definitions only, not values).
     * This can be useful for discovering what custom settings are available.
     *
     * @param HttpRestRequest $request The HTTP request object
     * @return Response
     */
    public function getFields(HttpRestRequest $request): Response
    {
        $fields = $this->service->getLayoutFields();
        $processingResult = new ProcessingResult();
        $processingResult->setData($fields);
        return RestControllerHelper::createProcessingResultResponse($request, $processingResult, 200, true);
    }
}
