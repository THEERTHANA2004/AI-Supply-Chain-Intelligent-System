# Supply Chain Data Dictionary

## 1. Product Data

| Field | Description |
|---|---|
| product_id | Unique product identifier |
| product_name | Product name |
| category | Product category |
| unit_price | Selling price per unit |

## 2. Demand Data

| Field | Description |
|---|---|
| date | Date of demand |
| product_id | Product identifier |
| region | Sales region |
| sales_quantity | Quantity sold |
| unit_price | Product price |
| promotion | Promotion indicator |
| inventory_level | Available inventory |
| lead_time_days | Supplier lead time |

## 3. Supplier Data

| Field | Description |
|---|---|
| supplier_id | Unique supplier identifier |
| supplier_name | Supplier name |
| delivery_time_days | Average delivery time |
| quality_rate | Supplier quality percentage |
| defect_rate | Defective item percentage |
| supplier_cost | Cost offered by supplier |
| reliability_score | Supplier reliability |
| location | Supplier location |

## 4. Inventory Data

| Field | Description |
|---|---|
| product_id | Product identifier |
| current_stock | Current inventory quantity |
| daily_demand | Average daily demand |
| lead_time_days | Lead time |
| holding_cost | Inventory holding cost |
| ordering_cost | Cost per order |
| unit_cost | Cost per product unit |

## 5. Workforce Data

| Field | Description |
|---|---|
| date | Date |
| department | Department name |
| workers_available | Available workers |
| workers_required | Required workers |
| workload | Workload level |
| overtime_hours | Overtime hours |
| absenteeism_rate | Employee absenteeism percentage |

## 6. Supply Chain Relationship Data

| Field | Description |
|---|---|
| source_id | Source entity |
| target_id | Target entity |
| relationship_type | Type of dependency |
| dependency_strength | Dependency strength |
| risk_level | Current risk level |

## 7. Prediction Data

| Field | Description |
|---|---|
| prediction_id | Unique prediction identifier |
| model_name | AI model used |
| prediction_type | Type of prediction |
| predicted_value | Model prediction |
| actual_value | Actual value when available |
| prediction_date | Date of prediction |

## 8. Recommendation Data

| Field | Description |
|---|---|
| recommendation_id | Unique recommendation identifier |
| decision_type | Type of decision |
| recommended_action | Suggested action |
| decision_score | Calculated decision score |
| created_at | Recommendation timestamp |