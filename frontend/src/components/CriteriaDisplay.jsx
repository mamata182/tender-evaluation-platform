function CriteriaDisplay({ tender, onNext }) {
  const criteria = tender.criteria || [];

  const grouped = {
    technical: criteria.filter((c) => c.category === "technical"),
    financial: criteria.filter((c) => c.category === "financial"),
    compliance: criteria.filter((c) => c.category === "compliance"),
  };

  return (
    <div>
      <h2>Extracted Tender Criteria</h2>
      <p className="subtext">
        AI extracted <strong>{criteria.length}</strong> criteria from{" "}
        <strong>{tender.title}</strong>
      </p>

      {Object.entries(grouped).map(([category, items]) => (
        <div className="section" key={category}>
          <h3>{category.toUpperCase()} Criteria</h3>

          {items.length === 0 ? (
            <p className="muted">No {category} criteria found</p>
          ) : (
            items.map((item, index) => (
              <div className="criteria-item" key={index}>
                <div className="criteria-text">{item.criterion_text}</div>

                <div className="criteria-meta">
                  <span className={item.is_mandatory ? "tag mandatory" : "tag optional"}>
                    {item.is_mandatory ? "Mandatory" : "Optional"}
                  </span>

                  {item.expected_value && (
                    <span className="tag">
                      {item.operator} {item.expected_value} {item.unit || ""}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      ))}

      <button className="btn primary" onClick={onNext}>
        Continue to Bidder Upload
      </button>
    </div>
  );
}

export default CriteriaDisplay;