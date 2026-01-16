<?php

/**
 * UserSettingLayoutService - Service for managing layout-based custom user settings.
 *
 * This service provides CRUD operations for user settings that are defined via
 * the Admin > Layouts system using the 'USR' form type. It allows administrators
 * to add custom fields without coding, and users to save their preferences.
 *
 * @package   OpenEMR
 * @link      https://plhi.lab.indianapolis.iu.edu
 * @author    Saptarshi Purkayastha
 * @copyright Copyright (c) 2025 PLHI
 * @license   https://github.com/iupui-soic/openemr/blob/master/LICENSE GNU General Public License 3
 */

namespace OpenEMR\Services\UserSettings;

use OpenEMR\Common\Database\QueryUtils;
use OpenEMR\Services\BaseService;
use OpenEMR\Validators\ProcessingResult;

class UserSettingLayoutService extends BaseService
{
    public const TABLE_NAME = 'user_setting_layout_data';
    public const LAYOUT_FORM_ID = 'USR';

    public function __construct()
    {
        parent::__construct(self::TABLE_NAME);
    }

    /**
     * Get all USR layout fields from layout_options
     *
     * @return array Array of layout field definitions
     */
    public function getLayoutFields(): array
    {
        $sql = "SELECT lo.*, lgp.grp_title as group_title
                FROM layout_options lo
                LEFT JOIN layout_group_properties lgp
                    ON lgp.grp_form_id = lo.form_id AND lgp.grp_group_id = lo.group_id
                WHERE lo.form_id = ? AND lo.uor > 0 AND lo.field_id != ''
                ORDER BY lo.group_id, lo.seq";

        $result = QueryUtils::fetchRecords($sql, [self::LAYOUT_FORM_ID]);
        return $result ?: [];
    }

    /**
     * Check if any USR layout fields are defined
     *
     * @return bool True if custom fields exist
     */
    public function hasCustomFields(): bool
    {
        $sql = "SELECT COUNT(*) as cnt FROM layout_options
                WHERE form_id = ? AND uor > 0 AND field_id != ''";
        $result = sqlQuery($sql, [self::LAYOUT_FORM_ID]);
        return ($result['cnt'] ?? 0) > 0;
    }

    /**
     * Get all custom settings for a user
     *
     * @param int $userId The user ID
     * @return array Array of field_id => field_value pairs
     */
    public function getAllUserSettings(int $userId): array
    {
        $sql = "SELECT field_id, field_value FROM " . self::TABLE_NAME . " WHERE user_id = ?";
        $result = QueryUtils::fetchRecords($sql, [$userId]);

        $settings = [];
        if ($result) {
            foreach ($result as $row) {
                $settings[$row['field_id']] = $row['field_value'];
            }
        }
        return $settings;
    }

    /**
     * Get a specific custom setting value for a user
     *
     * @param int $userId The user ID
     * @param string $fieldId The field ID
     * @param string|null $default Default value if not found
     * @return string|null The field value or default
     */
    public function getUserSettingValue(int $userId, string $fieldId, ?string $default = null): ?string
    {
        $sql = "SELECT field_value FROM " . self::TABLE_NAME . "
                WHERE user_id = ? AND field_id = ?";
        $result = sqlQuery($sql, [$userId, $fieldId]);
        return $result['field_value'] ?? $default;
    }

    /**
     * Get a setting value with layout field definition
     *
     * @param int $userId The user ID
     * @param string $fieldId The field ID
     * @return ProcessingResult Contains both field definition and current value
     */
    public function getUserSettingWithDefinition(int $userId, string $fieldId): ProcessingResult
    {
        $processingResult = new ProcessingResult();

        // Get the layout field definition
        $fieldDef = $this->getLayoutFieldDefinition($fieldId);
        if (empty($fieldDef)) {
            $processingResult->addValidationMessage("field_id", "Field not found in USR layout");
            return $processingResult;
        }

        // Get the current value
        $currentValue = $this->getUserSettingValue($userId, $fieldId);

        $data = [
            'field_id' => $fieldId,
            'field_value' => $currentValue,
            'default_value' => $fieldDef['default_value'] ?? '',
            'definition' => $fieldDef
        ];

        $processingResult->addData($data);
        return $processingResult;
    }

    /**
     * Set a custom setting value for a user
     *
     * @param int $userId The user ID
     * @param string $fieldId The field ID
     * @param string|null $value The value to set
     * @return ProcessingResult
     */
    public function setUserSettingValue(int $userId, string $fieldId, ?string $value): ProcessingResult
    {
        $processingResult = new ProcessingResult();

        // Verify the field exists in the USR layout
        $fieldDef = $this->getLayoutFieldDefinition($fieldId);
        if (empty($fieldDef)) {
            $processingResult->addValidationMessage("field_id", "Field not found in USR layout");
            return $processingResult;
        }

        // Check if entry exists
        $existing = sqlQuery(
            "SELECT id FROM " . self::TABLE_NAME . " WHERE user_id = ? AND field_id = ?",
            [$userId, $fieldId]
        );

        if (!empty($existing)) {
            // Update existing entry
            sqlStatement(
                "UPDATE " . self::TABLE_NAME . " SET field_value = ? WHERE id = ?",
                [$value, $existing['id']]
            );
        } else {
            // Insert new entry
            sqlStatement(
                "INSERT INTO " . self::TABLE_NAME . " (user_id, field_id, field_value) VALUES (?, ?, ?)",
                [$userId, $fieldId, $value]
            );
        }

        $processingResult->addData([
            'user_id' => $userId,
            'field_id' => $fieldId,
            'field_value' => $value
        ]);

        return $processingResult;
    }

    /**
     * Set multiple custom setting values for a user
     *
     * @param int $userId The user ID
     * @param array $settings Array of field_id => field_value pairs
     * @return ProcessingResult
     */
    public function setMultipleUserSettings(int $userId, array $settings): ProcessingResult
    {
        $processingResult = new ProcessingResult();

        foreach ($settings as $fieldId => $value) {
            $result = $this->setUserSettingValue($userId, $fieldId, $value);
            if ($result->hasErrors()) {
                foreach ($result->getValidationMessages() as $field => $messages) {
                    foreach ($messages as $message) {
                        $processingResult->addValidationMessage($field, $message);
                    }
                }
            }
        }

        if (!$processingResult->hasErrors()) {
            $processingResult->addData(['updated_count' => count($settings)]);
        }

        return $processingResult;
    }

    /**
     * Delete a custom setting for a user (reset to default)
     *
     * @param int $userId The user ID
     * @param string $fieldId The field ID
     * @return ProcessingResult
     */
    public function deleteUserSettingValue(int $userId, string $fieldId): ProcessingResult
    {
        $processingResult = new ProcessingResult();

        sqlStatement(
            "DELETE FROM " . self::TABLE_NAME . " WHERE user_id = ? AND field_id = ?",
            [$userId, $fieldId]
        );

        $processingResult->addData([
            'user_id' => $userId,
            'field_id' => $fieldId,
            'deleted' => true
        ]);

        return $processingResult;
    }

    /**
     * Delete all custom settings for a user
     *
     * @param int $userId The user ID
     * @return ProcessingResult
     */
    public function deleteAllUserSettings(int $userId): ProcessingResult
    {
        $processingResult = new ProcessingResult();

        $result = sqlStatement(
            "DELETE FROM " . self::TABLE_NAME . " WHERE user_id = ?",
            [$userId]
        );

        $processingResult->addData([
            'user_id' => $userId,
            'deleted' => true
        ]);

        return $processingResult;
    }

    /**
     * Get layout field definition by field_id
     *
     * @param string $fieldId The field ID
     * @return array|null The field definition or null if not found
     */
    public function getLayoutFieldDefinition(string $fieldId): ?array
    {
        $sql = "SELECT * FROM layout_options
                WHERE form_id = ? AND field_id = ?";
        $result = sqlQuery($sql, [self::LAYOUT_FORM_ID, $fieldId]);
        return $result ?: null;
    }

    /**
     * Get all settings for a user with their layout definitions (for API response)
     *
     * @param int $userId The user ID
     * @return ProcessingResult
     */
    public function getAllUserSettingsForApi(int $userId): ProcessingResult
    {
        $processingResult = new ProcessingResult();

        $layoutFields = $this->getLayoutFields();
        $userSettings = $this->getAllUserSettings($userId);

        $data = [];
        foreach ($layoutFields as $field) {
            $fieldId = $field['field_id'];
            $data[] = [
                'field_id' => $fieldId,
                'title' => $field['title'],
                'field_value' => $userSettings[$fieldId] ?? null,
                'default_value' => $field['default_value'] ?? '',
                'data_type' => $field['data_type'],
                'list_id' => $field['list_id'] ?? '',
                'description' => $field['description'] ?? ''
            ];
        }

        $processingResult->setData($data);
        return $processingResult;
    }
}
