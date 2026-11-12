import plotly.express as px
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Curso Superior", layout="wide", page_icon="🐍")
caminho_arquivo = "Tabela_3_Areas_gerais_de_formacao_na_graduacao.xlsx"


# Atividade ta pedindo os estados do sudeste etnão deixei somente essas opções.
# OBS: Não encontrei nenhum dado na tabela relacionado aos anos então deixei sem apesar da atividade estar pedindo.
estados_sudeste = ["Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo"]


@st.cache_data
def carregar_dados(caminho_arquivo):
    xls = pd.read_excel(caminho_arquivo, header=None, engine="calamine")
    xls_linhas = xls.iloc[3:36, 0:10].copy()
    dados_totais = []

    areas = {
        "Todas as áreas": {"Total": 1, "Homens": 2, "Mulheres": 3},
        "Ciência, Tecnologia, Engenharias e Matemática": {
            "Total": 4,
            "Homens": 5,
            "Mulheres": 6,
        },
        "Educação, Serviços pessoais, Saúde e Bem-estar": {
            "Total": 7,
            "Homens": 8,
            "Mulheres": 9,
        },
    }

    for _, linha in xls_linhas.iterrows():
        localidade = str(linha[0]).strip()

        for area, generos in areas.items():
            # Homens
            dados_totais.append(
                {
                    "Localidade": localidade,
                    "Areas": area,
                    "Sexo": "Masculino",
                    "Pessoas": int(linha[generos["Homens"]]),
                }
            )

            # Mulheres
            dados_totais.append(
                {
                    "Localidade": localidade,
                    "Areas": area,
                    "Sexo": "Feminino",
                    "Pessoas": int(linha[generos["Mulheres"]]),
                }
            )

    df_final = pd.DataFrame(dados_totais)

    return df_final


try:
    df = carregar_dados(caminho_arquivo)

    st.sidebar.header("🔍 Filtros")

    # Filtro por estados
    localidades_disponiveis = estados_sudeste
    localidades_selecionadas = st.sidebar.multiselect(
        "Selecione os estados:",
        options=localidades_disponiveis,
        default=estados_sudeste,
    )

    # Filtro por áreas
    areas_disponiveis = df["Areas"].unique().tolist()
    areas_selecionadas = st.sidebar.multiselect(
        "Selecione as áreas:",
        options=areas_disponiveis,
        default=areas_disponiveis[1:],
    )

    # Filtro por sexos
    sexos_disponiveis = df["Sexo"].unique().tolist()
    sexos_selecionados = st.sidebar.multiselect(
        "Selecione o Sexo:",
        options=sexos_disponiveis,
        default=["Masculino", "Feminino"],
    )

    st.title("📊 Indicador de Curso Superior")
    st.markdown(
        "Pessoas com nível superior completo no Sudeste, por área de formação e sexo."
    )

    if "Todas as áreas" in areas_selecionadas and len(areas_selecionadas) > 1:
        st.warning(
            "Caso queria selecionar todas as areas deixe somente selecionado o 'Todas as áreas' para evitar dados duplicados."
        )
        st.stop()

    df_filtrado = df[
        (df["Localidade"].isin(localidades_selecionadas))
        & (df["Areas"].isin(areas_selecionadas))
        & (df["Sexo"].isin(sexos_selecionados))
    ]

    # Exibição dos resultados com base nos filtros selecionados pelo user
    if not df_filtrado.empty:
        st.subheader("Dados em Tabela")

        colunas_para_exibir = ["Localidade", "Areas", "Sexo", "Pessoas"]

        st.dataframe(
            df_filtrado[colunas_para_exibir].reset_index(drop=True),
            use_container_width=True,
        )

        st.subheader("Gráficos")
        col1, col2 = st.columns(2)

        with col1:
            df_estados = df_filtrado.groupby("Localidade", as_index=False)[
                "Pessoas"
            ].sum()

            grafico_estados = px.bar(
                df_estados,
                x="Localidade",
                y="Pessoas",
                title="Pessoas com superior completo por estado",
                labels={"Localidade": "Estado"},
            )

            st.plotly_chart(grafico_estados, use_container_width=True)

        with col2:
            df_areas = df_filtrado.groupby(["Areas", "Sexo"], as_index=False)[
                "Pessoas"
            ].sum()

            totais = df_areas.groupby("Areas")["Pessoas"].transform("sum")

            df_areas["Percentual"] = (
                df_areas["Pessoas"].div(totais.where(totais > 0)).fillna(0) * 100
            )

            grafico_areas = px.bar(
                df_areas,
                x="Percentual",
                y="Areas",
                color="Sexo",
                orientation="h",
                barmode="stack",
                title="Proporção por sexo e área nos estados selecionados",
                text_auto=".1f",
                hover_data=["Pessoas"],
                labels={"Areas": "Área", "Percentual": "Participação (%)"},
            )

            grafico_areas.update_xaxes(range=[0, 100], ticksuffix="%")
            st.plotly_chart(grafico_areas, use_container_width=True)

        col1, col2 = st.columns(2)

        col1.metric(
            "Dados de pessoas no filtro atual",
            f"{df_filtrado['Pessoas'].sum():,.0f}".replace(",", "."),
        )

        df_mulheres = df[
            (df["Localidade"].isin(localidades_selecionadas))
            & (df["Areas"].isin(areas_selecionadas))
        ]

        total = df_mulheres["Pessoas"].sum()
        mulheres = df_mulheres.loc[df_mulheres["Sexo"] == "Feminino", "Pessoas"].sum()
        percentual_mulheres = 100 * mulheres / total if total else 0
        col2.metric("Mulheres: ambos os sexos como base", f"{percentual_mulheres:.1f}%")

    else:
        st.warning("Nenhum dado foi encontrado com a combinação de filtroas atual.")
except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
