

class CompanyServices:

    @staticmethod
    async def get_companies_from_query(self, query):
        companies = []

        for company, username in query:
            companies.append({
                'id': company.id,
                'company_name': company.company_name,
                'description': company.description,
                'owner': username,
                'visibility': company.visibility
            })

        return companies