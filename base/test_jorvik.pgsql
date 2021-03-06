PGDMP                         t           croce_rossa_test    9.4.9    9.4.9 @              0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                       false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                       false                       1262    119363    croce_rossa_test    DATABASE     �   CREATE DATABASE croce_rossa_test WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'it_IT.UTF-8' LC_CTYPE = 'it_IT.UTF-8';
     DROP DATABASE croce_rossa_test;
             postgres    false                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
             postgres    false                       0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                  postgres    false    8                       0    0    public    ACL     �   REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;
                  postgres    false    8                        3079    11861    plpgsql 	   EXTENSION     ?   CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
    DROP EXTENSION plpgsql;
                  false                        0    0    EXTENSION plpgsql    COMMENT     @   COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';
                       false    1                        3079    119364    postgis 	   EXTENSION     ;   CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
    DROP EXTENSION postgis;
                  false    8            !           0    0    EXTENSION postgis    COMMENT     g   COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';
                       false    2            �            1259    120651    anagrafica_appartenenza    TABLE       CREATE TABLE anagrafica_appartenenza (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    membro character varying(2) NOT NULL,
    terminazione character varying(1),
    persona_id integer NOT NULL,
    precedente_id integer,
    sede_id integer NOT NULL,
    vecchia_sede_id integer
);
 +   DROP TABLE public.anagrafica_appartenenza;
       public         postgres    false    8            �            1259    120654    anagrafica_appartenenza_id_seq    SEQUENCE     �   CREATE SEQUENCE anagrafica_appartenenza_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.anagrafica_appartenenza_id_seq;
       public       postgres    false    8    187            "           0    0    anagrafica_appartenenza_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE anagrafica_appartenenza_id_seq OWNED BY anagrafica_appartenenza.id;
            public       postgres    false    188            �            1259    120656    anagrafica_delega    TABLE     �  CREATE TABLE anagrafica_delega (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    tipo character varying(2) NOT NULL,
    oggetto_id integer NOT NULL,
    firmatario_id integer,
    oggetto_tipo_id integer,
    persona_id integer NOT NULL,
    CONSTRAINT anagrafica_delega_oggetto_id_check CHECK ((oggetto_id >= 0))
);
 %   DROP TABLE public.anagrafica_delega;
       public         postgres    false    8            �            1259    120660    anagrafica_delega_id_seq    SEQUENCE     z   CREATE SEQUENCE anagrafica_delega_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.anagrafica_delega_id_seq;
       public       postgres    false    189    8            #           0    0    anagrafica_delega_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE anagrafica_delega_id_seq OWNED BY anagrafica_delega.id;
            public       postgres    false    190            �            1259    120662    anagrafica_dimissione    TABLE     }  CREATE TABLE anagrafica_dimissione (
    id integer NOT NULL,
    motivo character varying(3) NOT NULL,
    info character varying(512) NOT NULL,
    appartenenza_id integer NOT NULL,
    persona_id integer NOT NULL,
    richiedente_id integer,
    sede_id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL
);
 )   DROP TABLE public.anagrafica_dimissione;
       public         postgres    false    8            �            1259    120668    anagrafica_dimissione_id_seq    SEQUENCE     ~   CREATE SEQUENCE anagrafica_dimissione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.anagrafica_dimissione_id_seq;
       public       postgres    false    191    8            $           0    0    anagrafica_dimissione_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE anagrafica_dimissione_id_seq OWNED BY anagrafica_dimissione.id;
            public       postgres    false    192            �            1259    120670    anagrafica_documento    TABLE       CREATE TABLE anagrafica_documento (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    tipo character varying(1) NOT NULL,
    file character varying(100) NOT NULL,
    persona_id integer NOT NULL
);
 (   DROP TABLE public.anagrafica_documento;
       public         postgres    false    8            �            1259    120673    anagrafica_documento_id_seq    SEQUENCE     }   CREATE SEQUENCE anagrafica_documento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.anagrafica_documento_id_seq;
       public       postgres    false    193    8            %           0    0    anagrafica_documento_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE anagrafica_documento_id_seq OWNED BY anagrafica_documento.id;
            public       postgres    false    194            �            1259    120675    anagrafica_estensione    TABLE     �  CREATE TABLE anagrafica_estensione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    protocollo_numero character varying(512),
    protocollo_data date,
    motivo character varying(4096),
    appartenenza_id integer,
    destinazione_id integer NOT NULL,
    persona_id integer NOT NULL,
    richiedente_id integer
);
 )   DROP TABLE public.anagrafica_estensione;
       public         postgres    false    8            �            1259    120681    anagrafica_estensione_id_seq    SEQUENCE     ~   CREATE SEQUENCE anagrafica_estensione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.anagrafica_estensione_id_seq;
       public       postgres    false    8    195            &           0    0    anagrafica_estensione_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE anagrafica_estensione_id_seq OWNED BY anagrafica_estensione.id;
            public       postgres    false    196            �            1259    120683    anagrafica_fototessera    TABLE     4  CREATE TABLE anagrafica_fototessera (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    file character varying(100) NOT NULL,
    persona_id integer NOT NULL
);
 *   DROP TABLE public.anagrafica_fototessera;
       public         postgres    false    8            �            1259    120686    anagrafica_fototessera_id_seq    SEQUENCE        CREATE SEQUENCE anagrafica_fototessera_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.anagrafica_fototessera_id_seq;
       public       postgres    false    197    8            '           0    0    anagrafica_fototessera_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE anagrafica_fototessera_id_seq OWNED BY anagrafica_fototessera.id;
            public       postgres    false    198            �            1259    120688    anagrafica_persona    TABLE     d  CREATE TABLE anagrafica_persona (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    vecchio_id integer,
    nome character varying(64) NOT NULL,
    cognome character varying(64) NOT NULL,
    codice_fiscale character varying(16) NOT NULL,
    data_nascita date,
    genere character varying(1) NOT NULL,
    stato character varying(1) NOT NULL,
    comune_nascita character varying(64) NOT NULL,
    provincia_nascita character varying(2) NOT NULL,
    stato_nascita character varying(2) NOT NULL,
    indirizzo_residenza character varying(512),
    comune_residenza character varying(64),
    provincia_residenza character varying(2),
    stato_residenza character varying(2) NOT NULL,
    cap_residenza character varying(16),
    email_contatto character varying(255) NOT NULL,
    note text,
    avatar character varying(100),
    privacy_contatti smallint NOT NULL,
    privacy_curriculum smallint NOT NULL,
    privacy_deleghe smallint NOT NULL,
    cm boolean NOT NULL,
    conoscenza character varying(2),
    iv boolean NOT NULL
);
 &   DROP TABLE public.anagrafica_persona;
       public         postgres    false    8            �            1259    120694    anagrafica_persona_id_seq    SEQUENCE     {   CREATE SEQUENCE anagrafica_persona_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.anagrafica_persona_id_seq;
       public       postgres    false    8    199            (           0    0    anagrafica_persona_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE anagrafica_persona_id_seq OWNED BY anagrafica_persona.id;
            public       postgres    false    200            �            1259    120696 $   anagrafica_provvedimentodisciplinare    TABLE       CREATE TABLE anagrafica_provvedimentodisciplinare (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    protocollo_data date,
    protocollo_numero character varying(512),
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    motivazione character varying(500) NOT NULL,
    tipo character varying(1) NOT NULL,
    persona_id integer NOT NULL,
    sede_id integer NOT NULL,
    registrato_da_id integer
);
 8   DROP TABLE public.anagrafica_provvedimentodisciplinare;
       public         postgres    false    8            �            1259    120702 +   anagrafica_provvedimentodisciplinare_id_seq    SEQUENCE     �   CREATE SEQUENCE anagrafica_provvedimentodisciplinare_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 B   DROP SEQUENCE public.anagrafica_provvedimentodisciplinare_id_seq;
       public       postgres    false    8    201            )           0    0 +   anagrafica_provvedimentodisciplinare_id_seq    SEQUENCE OWNED BY     m   ALTER SEQUENCE anagrafica_provvedimentodisciplinare_id_seq OWNED BY anagrafica_provvedimentodisciplinare.id;
            public       postgres    false    202            �            1259    120704    anagrafica_riserva    TABLE     �  CREATE TABLE anagrafica_riserva (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    appartenenza_id integer NOT NULL,
    motivo character varying(4096) NOT NULL,
    persona_id integer NOT NULL,
    protocollo_data date,
    protocollo_numero character varying(512)
);
 &   DROP TABLE public.anagrafica_riserva;
       public         postgres    false    8            �            1259    120710    anagrafica_riserva_id_seq    SEQUENCE     {   CREATE SEQUENCE anagrafica_riserva_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.anagrafica_riserva_id_seq;
       public       postgres    false    203    8            *           0    0    anagrafica_riserva_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE anagrafica_riserva_id_seq OWNED BY anagrafica_riserva.id;
            public       postgres    false    204            �            1259    120712    anagrafica_sede    TABLE     �  CREATE TABLE anagrafica_sede (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    nome character varying(64) NOT NULL,
    vecchio_id integer,
    estensione character varying(1) NOT NULL,
    tipo character varying(1) NOT NULL,
    telefono character varying(64) NOT NULL,
    fax character varying(64) NOT NULL,
    email character varying(64) NOT NULL,
    codice_fiscale character varying(32) NOT NULL,
    partita_iva character varying(32) NOT NULL,
    attiva boolean NOT NULL,
    slug character varying(50) NOT NULL,
    lft integer NOT NULL,
    rght integer NOT NULL,
    tree_id integer NOT NULL,
    level integer NOT NULL,
    genitore_id integer,
    locazione_id integer,
    pec character varying(64) NOT NULL,
    iban character varying(32) NOT NULL,
    sito_web character varying(200) NOT NULL,
    CONSTRAINT anagrafica_sede_level_check CHECK ((level >= 0)),
    CONSTRAINT anagrafica_sede_lft_check CHECK ((lft >= 0)),
    CONSTRAINT anagrafica_sede_rght_check CHECK ((rght >= 0)),
    CONSTRAINT anagrafica_sede_tree_id_check CHECK ((tree_id >= 0))
);
 #   DROP TABLE public.anagrafica_sede;
       public         postgres    false    8            �            1259    120722    anagrafica_sede_id_seq    SEQUENCE     x   CREATE SEQUENCE anagrafica_sede_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.anagrafica_sede_id_seq;
       public       postgres    false    8    205            +           0    0    anagrafica_sede_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE anagrafica_sede_id_seq OWNED BY anagrafica_sede.id;
            public       postgres    false    206            �            1259    120724    anagrafica_telefono    TABLE       CREATE TABLE anagrafica_telefono (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    numero character varying(16) NOT NULL,
    servizio boolean NOT NULL,
    persona_id integer NOT NULL
);
 '   DROP TABLE public.anagrafica_telefono;
       public         postgres    false    8            �            1259    120727    anagrafica_telefono_id_seq    SEQUENCE     |   CREATE SEQUENCE anagrafica_telefono_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.anagrafica_telefono_id_seq;
       public       postgres    false    207    8            ,           0    0    anagrafica_telefono_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE anagrafica_telefono_id_seq OWNED BY anagrafica_telefono.id;
            public       postgres    false    208            �            1259    120729    anagrafica_trasferimento    TABLE     �  CREATE TABLE anagrafica_trasferimento (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    protocollo_numero character varying(16),
    protocollo_data date,
    motivo character varying(2048),
    appartenenza_id integer,
    destinazione_id integer NOT NULL,
    persona_id integer NOT NULL,
    richiedente_id integer
);
 ,   DROP TABLE public.anagrafica_trasferimento;
       public         postgres    false    8            �            1259    120735    anagrafica_trasferimento_id_seq    SEQUENCE     �   CREATE SEQUENCE anagrafica_trasferimento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.anagrafica_trasferimento_id_seq;
       public       postgres    false    8    209            -           0    0    anagrafica_trasferimento_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE anagrafica_trasferimento_id_seq OWNED BY anagrafica_trasferimento.id;
            public       postgres    false    210            �            1259    120737    attivita_area    TABLE     	  CREATE TABLE attivita_area (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    nome character varying(256) NOT NULL,
    obiettivo smallint NOT NULL,
    sede_id integer NOT NULL
);
 !   DROP TABLE public.attivita_area;
       public         postgres    false    8            �            1259    120740    attivita_area_id_seq    SEQUENCE     v   CREATE SEQUENCE attivita_area_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.attivita_area_id_seq;
       public       postgres    false    211    8            .           0    0    attivita_area_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE attivita_area_id_seq OWNED BY attivita_area.id;
            public       postgres    false    212            �            1259    120742    attivita_attivita    TABLE     �  CREATE TABLE attivita_attivita (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    vecchio_id integer,
    nome character varying(255) NOT NULL,
    stato character varying(1) NOT NULL,
    apertura character varying(1) NOT NULL,
    descrizione text NOT NULL,
    area_id integer,
    estensione_id integer,
    locazione_id integer,
    sede_id integer NOT NULL,
    centrale_operativa character varying(1)
);
 %   DROP TABLE public.attivita_attivita;
       public         postgres    false    8            �            1259    120748    attivita_attivita_id_seq    SEQUENCE     z   CREATE SEQUENCE attivita_attivita_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.attivita_attivita_id_seq;
       public       postgres    false    8    213            /           0    0    attivita_attivita_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE attivita_attivita_id_seq OWNED BY attivita_attivita.id;
            public       postgres    false    214            �            1259    120750    attivita_partecipazione    TABLE     |  CREATE TABLE attivita_partecipazione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    stato character varying(1) NOT NULL,
    persona_id integer NOT NULL,
    turno_id integer NOT NULL,
    centrale_operativa boolean NOT NULL
);
 +   DROP TABLE public.attivita_partecipazione;
       public         postgres    false    8            �            1259    120753    attivita_partecipazione_id_seq    SEQUENCE     �   CREATE SEQUENCE attivita_partecipazione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.attivita_partecipazione_id_seq;
       public       postgres    false    215    8            0           0    0    attivita_partecipazione_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE attivita_partecipazione_id_seq OWNED BY attivita_partecipazione.id;
            public       postgres    false    216            �            1259    120755    attivita_turno    TABLE     �  CREATE TABLE attivita_turno (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    nome character varying(128) NOT NULL,
    prenotazione timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    minimo smallint NOT NULL,
    massimo smallint,
    attivita_id integer NOT NULL
);
 "   DROP TABLE public.attivita_turno;
       public         postgres    false    8            �            1259    120758    attivita_turno_id_seq    SEQUENCE     w   CREATE SEQUENCE attivita_turno_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.attivita_turno_id_seq;
       public       postgres    false    8    217            1           0    0    attivita_turno_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE attivita_turno_id_seq OWNED BY attivita_turno.id;
            public       postgres    false    218            �            1259    120760    autenticazione_utenza    TABLE     �  CREATE TABLE autenticazione_utenza (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    email character varying(254) NOT NULL,
    ultimo_accesso timestamp with time zone,
    ultimo_consenso timestamp with time zone,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    persona_id integer
);
 )   DROP TABLE public.autenticazione_utenza;
       public         postgres    false    8            �            1259    120763    autenticazione_utenza_groups    TABLE     �   CREATE TABLE autenticazione_utenza_groups (
    id integer NOT NULL,
    utenza_id integer NOT NULL,
    group_id integer NOT NULL
);
 0   DROP TABLE public.autenticazione_utenza_groups;
       public         postgres    false    8            �            1259    120766 #   autenticazione_utenza_groups_id_seq    SEQUENCE     �   CREATE SEQUENCE autenticazione_utenza_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 :   DROP SEQUENCE public.autenticazione_utenza_groups_id_seq;
       public       postgres    false    8    220            2           0    0 #   autenticazione_utenza_groups_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE autenticazione_utenza_groups_id_seq OWNED BY autenticazione_utenza_groups.id;
            public       postgres    false    221            �            1259    120768    autenticazione_utenza_id_seq    SEQUENCE     ~   CREATE SEQUENCE autenticazione_utenza_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.autenticazione_utenza_id_seq;
       public       postgres    false    8    219            3           0    0    autenticazione_utenza_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE autenticazione_utenza_id_seq OWNED BY autenticazione_utenza.id;
            public       postgres    false    222            �            1259    120770 &   autenticazione_utenza_user_permissions    TABLE     �   CREATE TABLE autenticazione_utenza_user_permissions (
    id integer NOT NULL,
    utenza_id integer NOT NULL,
    permission_id integer NOT NULL
);
 :   DROP TABLE public.autenticazione_utenza_user_permissions;
       public         postgres    false    8            �            1259    120773 -   autenticazione_utenza_user_permissions_id_seq    SEQUENCE     �   CREATE SEQUENCE autenticazione_utenza_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 D   DROP SEQUENCE public.autenticazione_utenza_user_permissions_id_seq;
       public       postgres    false    8    223            4           0    0 -   autenticazione_utenza_user_permissions_id_seq    SEQUENCE OWNED BY     q   ALTER SEQUENCE autenticazione_utenza_user_permissions_id_seq OWNED BY autenticazione_utenza_user_permissions.id;
            public       postgres    false    224            �            1259    120775 
   auth_group    TABLE     ^   CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);
    DROP TABLE public.auth_group;
       public         postgres    false    8            �            1259    120778    auth_group_id_seq    SEQUENCE     s   CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.auth_group_id_seq;
       public       postgres    false    8    225            5           0    0    auth_group_id_seq    SEQUENCE OWNED BY     9   ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;
            public       postgres    false    226            �            1259    120780    auth_group_permissions    TABLE     �   CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);
 *   DROP TABLE public.auth_group_permissions;
       public         postgres    false    8            �            1259    120783    auth_group_permissions_id_seq    SEQUENCE        CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.auth_group_permissions_id_seq;
       public       postgres    false    8    227            6           0    0    auth_group_permissions_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;
            public       postgres    false    228            �            1259    120785    auth_permission    TABLE     �   CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);
 #   DROP TABLE public.auth_permission;
       public         postgres    false    8            �            1259    120788    auth_permission_id_seq    SEQUENCE     x   CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.auth_permission_id_seq;
       public       postgres    false    8    229            7           0    0    auth_permission_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;
            public       postgres    false    230            �            1259    120790    base_allegato    TABLE     �  CREATE TABLE base_allegato (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    oggetto_id integer,
    file character varying(100) NOT NULL,
    nome character varying(255) NOT NULL,
    oggetto_tipo_id integer,
    scadenza timestamp with time zone,
    CONSTRAINT base_allegato_oggetto_id_check CHECK ((oggetto_id >= 0))
);
 !   DROP TABLE public.base_allegato;
       public         postgres    false    8            �            1259    120794    base_allegato_id_seq    SEQUENCE     v   CREATE SEQUENCE base_allegato_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.base_allegato_id_seq;
       public       postgres    false    8    231            8           0    0    base_allegato_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE base_allegato_id_seq OWNED BY base_allegato.id;
            public       postgres    false    232            �            1259    120796    base_autorizzazione    TABLE     C  CREATE TABLE base_autorizzazione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    concessa boolean,
    motivo_negazione character varying(512),
    oggetto_id integer NOT NULL,
    necessaria boolean NOT NULL,
    progressivo smallint NOT NULL,
    destinatario_ruolo character varying(16) NOT NULL,
    destinatario_oggetto_id integer NOT NULL,
    destinatario_oggetto_tipo_id integer,
    firmatario_id integer,
    oggetto_tipo_id integer,
    richiedente_id integer NOT NULL,
    CONSTRAINT base_autorizzazione_destinatario_oggetto_id_check CHECK ((destinatario_oggetto_id >= 0)),
    CONSTRAINT base_autorizzazione_oggetto_id_check CHECK ((oggetto_id >= 0)),
    CONSTRAINT base_autorizzazione_progressivo_check CHECK ((progressivo >= 0))
);
 '   DROP TABLE public.base_autorizzazione;
       public         postgres    false    8            �            1259    120805    base_autorizzazione_id_seq    SEQUENCE     |   CREATE SEQUENCE base_autorizzazione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.base_autorizzazione_id_seq;
       public       postgres    false    8    233            9           0    0    base_autorizzazione_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE base_autorizzazione_id_seq OWNED BY base_autorizzazione.id;
            public       postgres    false    234            �            1259    120807    base_locazione    TABLE     !  CREATE TABLE base_locazione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    indirizzo character varying(255) NOT NULL,
    geo geography(Point,4326) NOT NULL,
    via character varying(64) NOT NULL,
    civico character varying(16) NOT NULL,
    comune character varying(64) NOT NULL,
    provincia character varying(64) NOT NULL,
    regione character varying(64) NOT NULL,
    cap character varying(32) NOT NULL,
    stato character varying(2) NOT NULL
);
 "   DROP TABLE public.base_locazione;
       public         postgres    false    2    2    8    8    2    8    2    8    2    8    2    8    2    8    2    8    8            �            1259    120813    base_locazione_id_seq    SEQUENCE     w   CREATE SEQUENCE base_locazione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.base_locazione_id_seq;
       public       postgres    false    235    8            :           0    0    base_locazione_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE base_locazione_id_seq OWNED BY base_locazione.id;
            public       postgres    false    236            �            1259    120815    base_log    TABLE        CREATE TABLE base_log (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    azione character varying(1) NOT NULL,
    oggetto_repr character varying(1024),
    oggetto_app_label character varying(1024),
    oggetto_model character varying(1024),
    oggetto_pk integer,
    oggetto_campo character varying(64),
    valore_precedente character varying(4096),
    valore_successivo character varying(4096),
    persona_id integer
);
    DROP TABLE public.base_log;
       public         postgres    false    8            �            1259    120821    base_log_id_seq    SEQUENCE     q   CREATE SEQUENCE base_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.base_log_id_seq;
       public       postgres    false    8    237            ;           0    0    base_log_id_seq    SEQUENCE OWNED BY     5   ALTER SEQUENCE base_log_id_seq OWNED BY base_log.id;
            public       postgres    false    238            �            1259    120823 
   base_token    TABLE     0  CREATE TABLE base_token (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    codice character varying(128) NOT NULL,
    persona_id integer NOT NULL,
    redirect character varying(128),
    valido_ore integer NOT NULL
);
    DROP TABLE public.base_token;
       public         postgres    false    8            �            1259    120826    base_token_id_seq    SEQUENCE     s   CREATE SEQUENCE base_token_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.base_token_id_seq;
       public       postgres    false    239    8            <           0    0    base_token_id_seq    SEQUENCE OWNED BY     9   ALTER SEQUENCE base_token_id_seq OWNED BY base_token.id;
            public       postgres    false    240            �            1259    120828    centrale_operativa_reperibilita    TABLE     U  CREATE TABLE centrale_operativa_reperibilita (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    attivazione time without time zone NOT NULL,
    persona_id integer NOT NULL
);
 3   DROP TABLE public.centrale_operativa_reperibilita;
       public         postgres    false    8            �            1259    120831 &   centrale_operativa_reperibilita_id_seq    SEQUENCE     �   CREATE SEQUENCE centrale_operativa_reperibilita_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public.centrale_operativa_reperibilita_id_seq;
       public       postgres    false    8    241            =           0    0 &   centrale_operativa_reperibilita_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE centrale_operativa_reperibilita_id_seq OWNED BY centrale_operativa_reperibilita.id;
            public       postgres    false    242            �            1259    120833    centrale_operativa_turno    TABLE     y  CREATE TABLE centrale_operativa_turno (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    montato_data timestamp with time zone,
    smontato_data timestamp with time zone,
    montato_da_id integer,
    persona_id integer NOT NULL,
    smontato_da_id integer,
    turno_id integer NOT NULL
);
 ,   DROP TABLE public.centrale_operativa_turno;
       public         postgres    false    8            �            1259    120836    centrale_operativa_turno_id_seq    SEQUENCE     �   CREATE SEQUENCE centrale_operativa_turno_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.centrale_operativa_turno_id_seq;
       public       postgres    false    8    243            >           0    0    centrale_operativa_turno_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE centrale_operativa_turno_id_seq OWNED BY centrale_operativa_turno.id;
            public       postgres    false    244            �            1259    120838    curriculum_titolo    TABLE     �  CREATE TABLE curriculum_titolo (
    id integer NOT NULL,
    vecchio_id integer,
    tipo character varying(2) NOT NULL,
    richiede_conferma boolean NOT NULL,
    richiede_data_ottenimento boolean NOT NULL,
    richiede_luogo_ottenimento boolean NOT NULL,
    richiede_data_scadenza boolean NOT NULL,
    richiede_codice boolean NOT NULL,
    inseribile_in_autonomia boolean NOT NULL,
    nome character varying(255) NOT NULL
);
 %   DROP TABLE public.curriculum_titolo;
       public         postgres    false    8            �            1259    120841    curriculum_titolo_id_seq    SEQUENCE     z   CREATE SEQUENCE curriculum_titolo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.curriculum_titolo_id_seq;
       public       postgres    false    8    245            ?           0    0    curriculum_titolo_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE curriculum_titolo_id_seq OWNED BY curriculum_titolo.id;
            public       postgres    false    246            �            1259    120843    curriculum_titolopersonale    TABLE       CREATE TABLE curriculum_titolopersonale (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    data_ottenimento date,
    luogo_ottenimento character varying(255),
    data_scadenza date,
    codice character varying(128),
    codice_corso character varying(128),
    certificato boolean NOT NULL,
    certificato_da_id integer,
    persona_id integer NOT NULL,
    titolo_id integer NOT NULL
);
 .   DROP TABLE public.curriculum_titolopersonale;
       public         postgres    false    8            �            1259    120849 !   curriculum_titolopersonale_id_seq    SEQUENCE     �   CREATE SEQUENCE curriculum_titolopersonale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.curriculum_titolopersonale_id_seq;
       public       postgres    false    247    8            @           0    0 !   curriculum_titolopersonale_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE curriculum_titolopersonale_id_seq OWNED BY curriculum_titolopersonale.id;
            public       postgres    false    248            �            1259    120851    django_admin_log    TABLE     �  CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);
 $   DROP TABLE public.django_admin_log;
       public         postgres    false    8            �            1259    120858    django_admin_log_id_seq    SEQUENCE     y   CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.django_admin_log_id_seq;
       public       postgres    false    249    8            A           0    0    django_admin_log_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;
            public       postgres    false    250            �            1259    120860    django_content_type    TABLE     �   CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);
 '   DROP TABLE public.django_content_type;
       public         postgres    false    8            �            1259    120863    django_content_type_id_seq    SEQUENCE     |   CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.django_content_type_id_seq;
       public       postgres    false    8    251            B           0    0    django_content_type_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;
            public       postgres    false    252            �            1259    120865    django_cron_cronjoblog    TABLE     0  CREATE TABLE django_cron_cronjoblog (
    id integer NOT NULL,
    code character varying(64) NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    is_success boolean NOT NULL,
    message text NOT NULL,
    ran_at_time time without time zone
);
 *   DROP TABLE public.django_cron_cronjoblog;
       public         postgres    false    8            �            1259    120871    django_cron_cronjoblog_id_seq    SEQUENCE        CREATE SEQUENCE django_cron_cronjoblog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.django_cron_cronjoblog_id_seq;
       public       postgres    false    8    253            C           0    0    django_cron_cronjoblog_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE django_cron_cronjoblog_id_seq OWNED BY django_cron_cronjoblog.id;
            public       postgres    false    254            �            1259    120873    django_migrations    TABLE     �   CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);
 %   DROP TABLE public.django_migrations;
       public         postgres    false    8                        1259    120879    django_migrations_id_seq    SEQUENCE     z   CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.django_migrations_id_seq;
       public       postgres    false    8    255            D           0    0    django_migrations_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;
            public       postgres    false    256                       1259    120881    django_session    TABLE     �   CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);
 "   DROP TABLE public.django_session;
       public         postgres    false    8                       1259    120887    django_site    TABLE     �   CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);
    DROP TABLE public.django_site;
       public         postgres    false    8                       1259    120890    django_site_id_seq    SEQUENCE     t   CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.django_site_id_seq;
       public       postgres    false    258    8            E           0    0    django_site_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;
            public       postgres    false    259                       1259    120892    formazione_aspirante    TABLE     �   CREATE TABLE formazione_aspirante (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    raggio double precision,
    locazione_id integer,
    persona_id integer NOT NULL
);
 (   DROP TABLE public.formazione_aspirante;
       public         postgres    false    8                       1259    120895    formazione_aspirante_id_seq    SEQUENCE     }   CREATE SEQUENCE formazione_aspirante_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.formazione_aspirante_id_seq;
       public       postgres    false    8    260            F           0    0    formazione_aspirante_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE formazione_aspirante_id_seq OWNED BY formazione_aspirante.id;
            public       postgres    false    261                       1259    120897    formazione_assenzacorsobase    TABLE       CREATE TABLE formazione_assenzacorsobase (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    lezione_id integer NOT NULL,
    persona_id integer NOT NULL,
    registrata_da_id integer
);
 /   DROP TABLE public.formazione_assenzacorsobase;
       public         postgres    false    8                       1259    120900 "   formazione_assenzacorsobase_id_seq    SEQUENCE     �   CREATE SEQUENCE formazione_assenzacorsobase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.formazione_assenzacorsobase_id_seq;
       public       postgres    false    8    262            G           0    0 "   formazione_assenzacorsobase_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE formazione_assenzacorsobase_id_seq OWNED BY formazione_assenzacorsobase.id;
            public       postgres    false    263                       1259    120902    formazione_corsobase    TABLE     h  CREATE TABLE formazione_corsobase (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    stato character varying(1) NOT NULL,
    data_inizio timestamp with time zone NOT NULL,
    data_esame timestamp with time zone NOT NULL,
    progressivo smallint NOT NULL,
    anno smallint NOT NULL,
    descrizione text,
    locazione_id integer,
    sede_id integer NOT NULL,
    vecchio_id integer,
    data_attivazione date,
    data_convocazione date,
    op_attivazione character varying(255),
    op_convocazione character varying(255)
);
 (   DROP TABLE public.formazione_corsobase;
       public         postgres    false    8            	           1259    120908    formazione_corsobase_id_seq    SEQUENCE     }   CREATE SEQUENCE formazione_corsobase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.formazione_corsobase_id_seq;
       public       postgres    false    264    8            H           0    0    formazione_corsobase_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE formazione_corsobase_id_seq OWNED BY formazione_corsobase.id;
            public       postgres    false    265            
           1259    120910    formazione_lezionecorsobase    TABLE     H  CREATE TABLE formazione_lezionecorsobase (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    nome character varying(128) NOT NULL,
    corso_id integer NOT NULL
);
 /   DROP TABLE public.formazione_lezionecorsobase;
       public         postgres    false    8                       1259    120913 "   formazione_lezionecorsobase_id_seq    SEQUENCE     �   CREATE SEQUENCE formazione_lezionecorsobase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.formazione_lezionecorsobase_id_seq;
       public       postgres    false    266    8            I           0    0 "   formazione_lezionecorsobase_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE formazione_lezionecorsobase_id_seq OWNED BY formazione_lezionecorsobase.id;
            public       postgres    false    267                       1259    120915 "   formazione_partecipazionecorsobase    TABLE     �  CREATE TABLE formazione_partecipazionecorsobase (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    esito_esame character varying(2),
    ammissione character varying(2),
    motivo_non_ammissione character varying(1025),
    esito_parte_1 character varying(1),
    argomento_parte_1 character varying(1024),
    esito_parte_2 character varying(1),
    argomento_parte_2 character varying(1024),
    extra_1 boolean NOT NULL,
    extra_2 boolean NOT NULL,
    corso_id integer NOT NULL,
    persona_id integer NOT NULL,
    destinazione_id integer
);
 6   DROP TABLE public.formazione_partecipazionecorsobase;
       public         postgres    false    8                       1259    120921 )   formazione_partecipazionecorsobase_id_seq    SEQUENCE     �   CREATE SEQUENCE formazione_partecipazionecorsobase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 @   DROP SEQUENCE public.formazione_partecipazionecorsobase_id_seq;
       public       postgres    false    8    268            J           0    0 )   formazione_partecipazionecorsobase_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE formazione_partecipazionecorsobase_id_seq OWNED BY formazione_partecipazionecorsobase.id;
            public       postgres    false    269                       1259    120923    gruppi_appartenenza    TABLE       CREATE TABLE gruppi_appartenenza (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    motivo_negazione character varying(512),
    gruppo_id integer NOT NULL,
    negato_da_id integer,
    persona_id integer NOT NULL
);
 '   DROP TABLE public.gruppi_appartenenza;
       public         postgres    false    8                       1259    120929    gruppi_appartenenza_id_seq    SEQUENCE     |   CREATE SEQUENCE gruppi_appartenenza_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.gruppi_appartenenza_id_seq;
       public       postgres    false    8    270            K           0    0    gruppi_appartenenza_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE gruppi_appartenenza_id_seq OWNED BY gruppi_appartenenza.id;
            public       postgres    false    271                       1259    120931    gruppi_gruppo    TABLE     d  CREATE TABLE gruppi_gruppo (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    estensione character varying(1) NOT NULL,
    nome character varying(255) NOT NULL,
    obiettivo integer NOT NULL,
    area_id integer,
    attivita_id integer,
    sede_id integer NOT NULL
);
 !   DROP TABLE public.gruppi_gruppo;
       public         postgres    false    8                       1259    120934    gruppi_gruppo_id_seq    SEQUENCE     v   CREATE SEQUENCE gruppi_gruppo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.gruppi_gruppo_id_seq;
       public       postgres    false    8    272            L           0    0    gruppi_gruppo_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE gruppi_gruppo_id_seq OWNED BY gruppi_gruppo.id;
            public       postgres    false    273                       1259    120936    patenti_elemento    TABLE     �   CREATE TABLE patenti_elemento (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL
);
 $   DROP TABLE public.patenti_elemento;
       public         postgres    false    8                       1259    120939    patenti_elemento_id_seq    SEQUENCE     y   CREATE SEQUENCE patenti_elemento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.patenti_elemento_id_seq;
       public       postgres    false    8    274            M           0    0    patenti_elemento_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE patenti_elemento_id_seq OWNED BY patenti_elemento.id;
            public       postgres    false    275                       1259    120941    patenti_patente    TABLE     �   CREATE TABLE patenti_patente (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    tipo character varying(2) NOT NULL
);
 #   DROP TABLE public.patenti_patente;
       public         postgres    false    8                       1259    120944    patenti_patente_id_seq    SEQUENCE     x   CREATE SEQUENCE patenti_patente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.patenti_patente_id_seq;
       public       postgres    false    8    276            N           0    0    patenti_patente_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE patenti_patente_id_seq OWNED BY patenti_patente.id;
            public       postgres    false    277                       1259    120946    posta_destinatario    TABLE     I  CREATE TABLE posta_destinatario (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inviato boolean NOT NULL,
    tentativo timestamp with time zone,
    errore character varying(256),
    messaggio_id integer NOT NULL,
    persona_id integer
);
 &   DROP TABLE public.posta_destinatario;
       public         postgres    false    8                       1259    120949    posta_destinatario_id_seq    SEQUENCE     {   CREATE SEQUENCE posta_destinatario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.posta_destinatario_id_seq;
       public       postgres    false    8    278            O           0    0    posta_destinatario_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE posta_destinatario_id_seq OWNED BY posta_destinatario.id;
            public       postgres    false    279                       1259    120951    posta_messaggio    TABLE     s  CREATE TABLE posta_messaggio (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    oggetto character varying(256) NOT NULL,
    corpo text NOT NULL,
    ultimo_tentativo timestamp with time zone,
    terminato timestamp with time zone,
    mittente_id integer,
    rispondi_a_id integer
);
 #   DROP TABLE public.posta_messaggio;
       public         postgres    false    8                       1259    120957    posta_messaggio_id_seq    SEQUENCE     x   CREATE SEQUENCE posta_messaggio_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.posta_messaggio_id_seq;
       public       postgres    false    280    8            P           0    0    posta_messaggio_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE posta_messaggio_id_seq OWNED BY posta_messaggio.id;
            public       postgres    false    281                       1259    120959    sangue_donatore    TABLE     �  CREATE TABLE sangue_donatore (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    gruppo_sanguigno character varying(3) NOT NULL,
    fattore_rh character varying(2),
    fanotipo_rh character varying(8),
    kell character varying(16),
    codice_sit character varying(32),
    persona_id integer NOT NULL,
    sede_sit_id integer
);
 #   DROP TABLE public.sangue_donatore;
       public         postgres    false    8                       1259    120962    sangue_donatore_id_seq    SEQUENCE     x   CREATE SEQUENCE sangue_donatore_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.sangue_donatore_id_seq;
       public       postgres    false    8    282            Q           0    0    sangue_donatore_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE sangue_donatore_id_seq OWNED BY sangue_donatore.id;
            public       postgres    false    283                       1259    120964    sangue_donazione    TABLE     Y  CREATE TABLE sangue_donazione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    confermata boolean NOT NULL,
    ritirata boolean NOT NULL,
    tipo character varying(2) NOT NULL,
    data date NOT NULL,
    persona_id integer NOT NULL,
    sede_id integer
);
 $   DROP TABLE public.sangue_donazione;
       public         postgres    false    8                       1259    120967    sangue_donazione_id_seq    SEQUENCE     y   CREATE SEQUENCE sangue_donazione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sangue_donazione_id_seq;
       public       postgres    false    284    8            R           0    0    sangue_donazione_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE sangue_donazione_id_seq OWNED BY sangue_donazione.id;
            public       postgres    false    285                       1259    120969    sangue_merito    TABLE       CREATE TABLE sangue_merito (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    donazione character varying(1) NOT NULL,
    merito character varying(8) NOT NULL,
    persona_id integer NOT NULL
);
 !   DROP TABLE public.sangue_merito;
       public         postgres    false    8                       1259    120972    sangue_merito_id_seq    SEQUENCE     v   CREATE SEQUENCE sangue_merito_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.sangue_merito_id_seq;
       public       postgres    false    8    286            S           0    0    sangue_merito_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE sangue_merito_id_seq OWNED BY sangue_merito.id;
            public       postgres    false    287                        1259    120974    sangue_sede    TABLE     �   CREATE TABLE sangue_sede (
    id integer NOT NULL,
    citta character varying(32) NOT NULL,
    provincia character varying(32) NOT NULL,
    regione character varying(32) NOT NULL,
    nome character varying(255) NOT NULL
);
    DROP TABLE public.sangue_sede;
       public         postgres    false    8            !           1259    120977    sangue_sede_id_seq    SEQUENCE     t   CREATE SEQUENCE sangue_sede_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.sangue_sede_id_seq;
       public       postgres    false    8    288            T           0    0    sangue_sede_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE sangue_sede_id_seq OWNED BY sangue_sede.id;
            public       postgres    false    289            "           1259    120979    social_commento    TABLE     g  CREATE TABLE social_commento (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    commento text NOT NULL,
    oggetto_id integer NOT NULL,
    autore_id integer NOT NULL,
    oggetto_tipo_id integer,
    CONSTRAINT social_commento_oggetto_id_check CHECK ((oggetto_id >= 0))
);
 #   DROP TABLE public.social_commento;
       public         postgres    false    8            #           1259    120986    social_commento_id_seq    SEQUENCE     x   CREATE SEQUENCE social_commento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.social_commento_id_seq;
       public       postgres    false    8    290            U           0    0    social_commento_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE social_commento_id_seq OWNED BY social_commento.id;
            public       postgres    false    291            $           1259    120988    social_giudizio    TABLE     j  CREATE TABLE social_giudizio (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    positivo boolean NOT NULL,
    oggetto_id integer NOT NULL,
    autore_id integer NOT NULL,
    oggetto_tipo_id integer,
    CONSTRAINT social_giudizio_oggetto_id_check CHECK ((oggetto_id >= 0))
);
 #   DROP TABLE public.social_giudizio;
       public         postgres    false    8            %           1259    120992    social_giudizio_id_seq    SEQUENCE     x   CREATE SEQUENCE social_giudizio_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.social_giudizio_id_seq;
       public       postgres    false    8    292            V           0    0    social_giudizio_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE social_giudizio_id_seq OWNED BY social_giudizio.id;
            public       postgres    false    293            &           1259    120994    thumbnail_kvstore    TABLE     e   CREATE TABLE thumbnail_kvstore (
    key character varying(200) NOT NULL,
    value text NOT NULL
);
 %   DROP TABLE public.thumbnail_kvstore;
       public         postgres    false    8            '           1259    121000    ufficio_soci_quota    TABLE     �  CREATE TABLE ufficio_soci_quota (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    progressivo integer NOT NULL,
    anno smallint NOT NULL,
    data_versamento date NOT NULL,
    data_annullamento date,
    stato character varying(1) NOT NULL,
    tipo character varying(1) NOT NULL,
    importo double precision NOT NULL,
    importo_extra double precision NOT NULL,
    causale character varying(512) NOT NULL,
    causale_extra character varying(512) NOT NULL,
    annullato_da_id integer,
    appartenenza_id integer,
    persona_id integer NOT NULL,
    registrato_da_id integer,
    sede_id integer NOT NULL,
    vecchio_id integer
);
 &   DROP TABLE public.ufficio_soci_quota;
       public         postgres    false    8            (           1259    121006    ufficio_soci_quota_id_seq    SEQUENCE     {   CREATE SEQUENCE ufficio_soci_quota_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.ufficio_soci_quota_id_seq;
       public       postgres    false    8    295            W           0    0    ufficio_soci_quota_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE ufficio_soci_quota_id_seq OWNED BY ufficio_soci_quota.id;
            public       postgres    false    296            )           1259    121008    ufficio_soci_tesseramento    TABLE     �  CREATE TABLE ufficio_soci_tesseramento (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    stato character varying(1) NOT NULL,
    anno smallint NOT NULL,
    inizio date NOT NULL,
    quota_attivo double precision NOT NULL,
    quota_ordinario double precision NOT NULL,
    quota_benemerito double precision NOT NULL,
    quota_aspirante double precision NOT NULL,
    quota_sostenitore double precision NOT NULL
);
 -   DROP TABLE public.ufficio_soci_tesseramento;
       public         postgres    false    8            *           1259    121011     ufficio_soci_tesseramento_id_seq    SEQUENCE     �   CREATE SEQUENCE ufficio_soci_tesseramento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.ufficio_soci_tesseramento_id_seq;
       public       postgres    false    8    297            X           0    0     ufficio_soci_tesseramento_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE ufficio_soci_tesseramento_id_seq OWNED BY ufficio_soci_tesseramento.id;
            public       postgres    false    298            +           1259    121013    ufficio_soci_tesserino    TABLE     �  CREATE TABLE ufficio_soci_tesserino (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    tipo_richiesta character varying(3) NOT NULL,
    stato_richiesta character varying(3) NOT NULL,
    motivo_richiesta character varying(512),
    motivo_rifiutato character varying(512),
    stato_emissione character varying(8),
    valido boolean NOT NULL,
    codice character varying(13),
    data_conferma timestamp with time zone,
    data_riconsegna timestamp with time zone,
    confermato_da_id integer,
    emesso_da_id integer NOT NULL,
    persona_id integer NOT NULL,
    richiesto_da_id integer NOT NULL,
    riconsegnato_a_id integer
);
 *   DROP TABLE public.ufficio_soci_tesserino;
       public         postgres    false    8            ,           1259    121019    ufficio_soci_tesserino_id_seq    SEQUENCE        CREATE SEQUENCE ufficio_soci_tesserino_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.ufficio_soci_tesserino_id_seq;
       public       postgres    false    8    299            Y           0    0    ufficio_soci_tesserino_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE ufficio_soci_tesserino_id_seq OWNED BY ufficio_soci_tesserino.id;
            public       postgres    false    300            -           1259    121021    veicoli_autoparco    TABLE     a  CREATE TABLE veicoli_autoparco (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    estensione character varying(1) NOT NULL,
    nome character varying(256) NOT NULL,
    telefono character varying(64) NOT NULL,
    locazione_id integer,
    sede_id integer NOT NULL
);
 %   DROP TABLE public.veicoli_autoparco;
       public         postgres    false    8            .           1259    121024    veicoli_autoparco_id_seq    SEQUENCE     z   CREATE SEQUENCE veicoli_autoparco_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.veicoli_autoparco_id_seq;
       public       postgres    false    8    301            Z           0    0    veicoli_autoparco_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE veicoli_autoparco_id_seq OWNED BY veicoli_autoparco.id;
            public       postgres    false    302            /           1259    121026    veicoli_collocazione    TABLE     V  CREATE TABLE veicoli_collocazione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    autoparco_id integer NOT NULL,
    creato_da_id integer,
    veicolo_id integer NOT NULL
);
 (   DROP TABLE public.veicoli_collocazione;
       public         postgres    false    8            0           1259    121029    veicoli_collocazione_id_seq    SEQUENCE     }   CREATE SEQUENCE veicoli_collocazione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.veicoli_collocazione_id_seq;
       public       postgres    false    303    8            [           0    0    veicoli_collocazione_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE veicoli_collocazione_id_seq OWNED BY veicoli_collocazione.id;
            public       postgres    false    304            1           1259    121031    veicoli_fermotecnico    TABLE     _  CREATE TABLE veicoli_fermotecnico (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    inizio timestamp with time zone NOT NULL,
    fine timestamp with time zone,
    motivo character varying(512) NOT NULL,
    creato_da_id integer,
    veicolo_id integer NOT NULL
);
 (   DROP TABLE public.veicoli_fermotecnico;
       public         postgres    false    8            2           1259    121037    veicoli_fermotecnico_id_seq    SEQUENCE     }   CREATE SEQUENCE veicoli_fermotecnico_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.veicoli_fermotecnico_id_seq;
       public       postgres    false    8    305            \           0    0    veicoli_fermotecnico_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE veicoli_fermotecnico_id_seq OWNED BY veicoli_fermotecnico.id;
            public       postgres    false    306            3           1259    121039    veicoli_manutenzione    TABLE       CREATE TABLE veicoli_manutenzione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    tipo character varying(1) NOT NULL,
    data date NOT NULL,
    descrizione text,
    km integer NOT NULL,
    manutentore character varying(512) NOT NULL,
    numero_fattura character varying(64) NOT NULL,
    costo double precision NOT NULL,
    creato_da_id integer,
    veicolo_id integer NOT NULL,
    CONSTRAINT veicoli_manutenzione_km_check CHECK ((km >= 0))
);
 (   DROP TABLE public.veicoli_manutenzione;
       public         postgres    false    8            4           1259    121046    veicoli_manutenzione_id_seq    SEQUENCE     }   CREATE SEQUENCE veicoli_manutenzione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.veicoli_manutenzione_id_seq;
       public       postgres    false    8    307            ]           0    0    veicoli_manutenzione_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE veicoli_manutenzione_id_seq OWNED BY veicoli_manutenzione.id;
            public       postgres    false    308            5           1259    121048    veicoli_rifornimento    TABLE     K  CREATE TABLE veicoli_rifornimento (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    data timestamp with time zone NOT NULL,
    contachilometri integer NOT NULL,
    costo double precision NOT NULL,
    consumo_carburante double precision NOT NULL,
    presso character varying(1),
    contalitri double precision,
    ricevuta character varying(32),
    veicolo_id integer NOT NULL,
    creato_da_id integer,
    CONSTRAINT veicoli_rifornimento_contachilometri_check CHECK ((contachilometri >= 0))
);
 (   DROP TABLE public.veicoli_rifornimento;
       public         postgres    false    8            6           1259    121052    veicoli_rifornimento_id_seq    SEQUENCE     }   CREATE SEQUENCE veicoli_rifornimento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.veicoli_rifornimento_id_seq;
       public       postgres    false    309    8            ^           0    0    veicoli_rifornimento_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE veicoli_rifornimento_id_seq OWNED BY veicoli_rifornimento.id;
            public       postgres    false    310            7           1259    121054    veicoli_segnalazione    TABLE     $  CREATE TABLE veicoli_segnalazione (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    descrizione text NOT NULL,
    autore_id integer NOT NULL,
    manutenzione_id integer,
    veicolo_id integer NOT NULL
);
 (   DROP TABLE public.veicoli_segnalazione;
       public         postgres    false    8            8           1259    121060    veicoli_segnalazione_id_seq    SEQUENCE     }   CREATE SEQUENCE veicoli_segnalazione_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.veicoli_segnalazione_id_seq;
       public       postgres    false    311    8            _           0    0    veicoli_segnalazione_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE veicoli_segnalazione_id_seq OWNED BY veicoli_segnalazione.id;
            public       postgres    false    312            9           1259    121062    veicoli_veicolo    TABLE     �  CREATE TABLE veicoli_veicolo (
    id integer NOT NULL,
    creazione timestamp with time zone NOT NULL,
    ultima_modifica timestamp with time zone NOT NULL,
    stato character varying(2) NOT NULL,
    libretto character varying(32) NOT NULL,
    targa character varying(16) NOT NULL,
    prima_immatricolazione date NOT NULL,
    proprietario_cognome character varying(127) NOT NULL,
    proprietario_nome character varying(127) NOT NULL,
    proprietario_indirizzo character varying(127) NOT NULL,
    pneumatici_anteriori character varying(255) NOT NULL,
    pneumatici_posteriori character varying(255) NOT NULL,
    pneumatici_alt_anteriori character varying(255),
    pneumatici_alt_posteriori character varying(255),
    cambio character varying(32) NOT NULL,
    lunghezza double precision,
    larghezza double precision,
    sbalzo double precision,
    tara integer,
    marca character varying(32) NOT NULL,
    modello character varying(32) NOT NULL,
    telaio character varying(64),
    massa_max integer NOT NULL,
    data_immatricolazione date NOT NULL,
    categoria character varying(128) NOT NULL,
    destinazione character varying(128) NOT NULL,
    carrozzeria character varying(128) NOT NULL,
    omologazione character varying(32),
    num_assi integer NOT NULL,
    rimorchio_frenato double precision,
    cilindrata integer NOT NULL,
    potenza_massima integer NOT NULL,
    alimentazione character varying(1),
    posti integer NOT NULL,
    regime integer NOT NULL,
    card_rifornimento character varying(64),
    selettiva_radio character varying(64),
    telepass character varying(64),
    intervallo_revisione integer NOT NULL,
    CONSTRAINT veicoli_veicolo_cilindrata_check CHECK ((cilindrata >= 0)),
    CONSTRAINT veicoli_veicolo_intervallo_revisione_check CHECK ((intervallo_revisione >= 0)),
    CONSTRAINT veicoli_veicolo_massa_max_check CHECK ((massa_max >= 0)),
    CONSTRAINT veicoli_veicolo_num_assi_check CHECK ((num_assi >= 0)),
    CONSTRAINT veicoli_veicolo_posti_check CHECK ((posti >= 0)),
    CONSTRAINT veicoli_veicolo_potenza_massima_check CHECK ((potenza_massima >= 0)),
    CONSTRAINT veicoli_veicolo_regime_check CHECK ((regime >= 0)),
    CONSTRAINT veicoli_veicolo_tara_check CHECK ((tara >= 0))
);
 #   DROP TABLE public.veicoli_veicolo;
       public         postgres    false    8            :           1259    121076    veicoli_veicolo_id_seq    SEQUENCE     x   CREATE SEQUENCE veicoli_veicolo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.veicoli_veicolo_id_seq;
       public       postgres    false    313    8            `           0    0    veicoli_veicolo_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE veicoli_veicolo_id_seq OWNED BY veicoli_veicolo.id;
            public       postgres    false    314            �           2604    121078    id    DEFAULT     z   ALTER TABLE ONLY anagrafica_appartenenza ALTER COLUMN id SET DEFAULT nextval('anagrafica_appartenenza_id_seq'::regclass);
 I   ALTER TABLE public.anagrafica_appartenenza ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    188    187            �           2604    121079    id    DEFAULT     n   ALTER TABLE ONLY anagrafica_delega ALTER COLUMN id SET DEFAULT nextval('anagrafica_delega_id_seq'::regclass);
 C   ALTER TABLE public.anagrafica_delega ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    190    189            �           2604    121080    id    DEFAULT     v   ALTER TABLE ONLY anagrafica_dimissione ALTER COLUMN id SET DEFAULT nextval('anagrafica_dimissione_id_seq'::regclass);
 G   ALTER TABLE public.anagrafica_dimissione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    192    191            �           2604    121081    id    DEFAULT     t   ALTER TABLE ONLY anagrafica_documento ALTER COLUMN id SET DEFAULT nextval('anagrafica_documento_id_seq'::regclass);
 F   ALTER TABLE public.anagrafica_documento ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    194    193            �           2604    121082    id    DEFAULT     v   ALTER TABLE ONLY anagrafica_estensione ALTER COLUMN id SET DEFAULT nextval('anagrafica_estensione_id_seq'::regclass);
 G   ALTER TABLE public.anagrafica_estensione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    196    195            �           2604    121083    id    DEFAULT     x   ALTER TABLE ONLY anagrafica_fototessera ALTER COLUMN id SET DEFAULT nextval('anagrafica_fototessera_id_seq'::regclass);
 H   ALTER TABLE public.anagrafica_fototessera ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    198    197            �           2604    121084    id    DEFAULT     p   ALTER TABLE ONLY anagrafica_persona ALTER COLUMN id SET DEFAULT nextval('anagrafica_persona_id_seq'::regclass);
 D   ALTER TABLE public.anagrafica_persona ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    200    199            �           2604    121085    id    DEFAULT     �   ALTER TABLE ONLY anagrafica_provvedimentodisciplinare ALTER COLUMN id SET DEFAULT nextval('anagrafica_provvedimentodisciplinare_id_seq'::regclass);
 V   ALTER TABLE public.anagrafica_provvedimentodisciplinare ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    202    201            �           2604    121086    id    DEFAULT     p   ALTER TABLE ONLY anagrafica_riserva ALTER COLUMN id SET DEFAULT nextval('anagrafica_riserva_id_seq'::regclass);
 D   ALTER TABLE public.anagrafica_riserva ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    204    203            �           2604    121087    id    DEFAULT     j   ALTER TABLE ONLY anagrafica_sede ALTER COLUMN id SET DEFAULT nextval('anagrafica_sede_id_seq'::regclass);
 A   ALTER TABLE public.anagrafica_sede ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    206    205            �           2604    121088    id    DEFAULT     r   ALTER TABLE ONLY anagrafica_telefono ALTER COLUMN id SET DEFAULT nextval('anagrafica_telefono_id_seq'::regclass);
 E   ALTER TABLE public.anagrafica_telefono ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    208    207            �           2604    121089    id    DEFAULT     |   ALTER TABLE ONLY anagrafica_trasferimento ALTER COLUMN id SET DEFAULT nextval('anagrafica_trasferimento_id_seq'::regclass);
 J   ALTER TABLE public.anagrafica_trasferimento ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    210    209            �           2604    121090    id    DEFAULT     f   ALTER TABLE ONLY attivita_area ALTER COLUMN id SET DEFAULT nextval('attivita_area_id_seq'::regclass);
 ?   ALTER TABLE public.attivita_area ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    212    211            �           2604    121091    id    DEFAULT     n   ALTER TABLE ONLY attivita_attivita ALTER COLUMN id SET DEFAULT nextval('attivita_attivita_id_seq'::regclass);
 C   ALTER TABLE public.attivita_attivita ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    214    213            �           2604    121092    id    DEFAULT     z   ALTER TABLE ONLY attivita_partecipazione ALTER COLUMN id SET DEFAULT nextval('attivita_partecipazione_id_seq'::regclass);
 I   ALTER TABLE public.attivita_partecipazione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    216    215            �           2604    121093    id    DEFAULT     h   ALTER TABLE ONLY attivita_turno ALTER COLUMN id SET DEFAULT nextval('attivita_turno_id_seq'::regclass);
 @   ALTER TABLE public.attivita_turno ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    218    217            �           2604    121094    id    DEFAULT     v   ALTER TABLE ONLY autenticazione_utenza ALTER COLUMN id SET DEFAULT nextval('autenticazione_utenza_id_seq'::regclass);
 G   ALTER TABLE public.autenticazione_utenza ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    222    219            �           2604    121095    id    DEFAULT     �   ALTER TABLE ONLY autenticazione_utenza_groups ALTER COLUMN id SET DEFAULT nextval('autenticazione_utenza_groups_id_seq'::regclass);
 N   ALTER TABLE public.autenticazione_utenza_groups ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    221    220            �           2604    121096    id    DEFAULT     �   ALTER TABLE ONLY autenticazione_utenza_user_permissions ALTER COLUMN id SET DEFAULT nextval('autenticazione_utenza_user_permissions_id_seq'::regclass);
 X   ALTER TABLE public.autenticazione_utenza_user_permissions ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    224    223            �           2604    121097    id    DEFAULT     `   ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);
 <   ALTER TABLE public.auth_group ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    226    225            �           2604    121098    id    DEFAULT     x   ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);
 H   ALTER TABLE public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    228    227            �           2604    121099    id    DEFAULT     j   ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);
 A   ALTER TABLE public.auth_permission ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    230    229            �           2604    121100    id    DEFAULT     f   ALTER TABLE ONLY base_allegato ALTER COLUMN id SET DEFAULT nextval('base_allegato_id_seq'::regclass);
 ?   ALTER TABLE public.base_allegato ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    232    231            �           2604    121101    id    DEFAULT     r   ALTER TABLE ONLY base_autorizzazione ALTER COLUMN id SET DEFAULT nextval('base_autorizzazione_id_seq'::regclass);
 E   ALTER TABLE public.base_autorizzazione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    234    233            �           2604    121102    id    DEFAULT     h   ALTER TABLE ONLY base_locazione ALTER COLUMN id SET DEFAULT nextval('base_locazione_id_seq'::regclass);
 @   ALTER TABLE public.base_locazione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    236    235            �           2604    121103    id    DEFAULT     \   ALTER TABLE ONLY base_log ALTER COLUMN id SET DEFAULT nextval('base_log_id_seq'::regclass);
 :   ALTER TABLE public.base_log ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    238    237            �           2604    121104    id    DEFAULT     `   ALTER TABLE ONLY base_token ALTER COLUMN id SET DEFAULT nextval('base_token_id_seq'::regclass);
 <   ALTER TABLE public.base_token ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    240    239            �           2604    121105    id    DEFAULT     �   ALTER TABLE ONLY centrale_operativa_reperibilita ALTER COLUMN id SET DEFAULT nextval('centrale_operativa_reperibilita_id_seq'::regclass);
 Q   ALTER TABLE public.centrale_operativa_reperibilita ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    242    241            �           2604    121106    id    DEFAULT     |   ALTER TABLE ONLY centrale_operativa_turno ALTER COLUMN id SET DEFAULT nextval('centrale_operativa_turno_id_seq'::regclass);
 J   ALTER TABLE public.centrale_operativa_turno ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    244    243            �           2604    121107    id    DEFAULT     n   ALTER TABLE ONLY curriculum_titolo ALTER COLUMN id SET DEFAULT nextval('curriculum_titolo_id_seq'::regclass);
 C   ALTER TABLE public.curriculum_titolo ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    246    245            �           2604    121108    id    DEFAULT     �   ALTER TABLE ONLY curriculum_titolopersonale ALTER COLUMN id SET DEFAULT nextval('curriculum_titolopersonale_id_seq'::regclass);
 L   ALTER TABLE public.curriculum_titolopersonale ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    248    247            �           2604    121109    id    DEFAULT     l   ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);
 B   ALTER TABLE public.django_admin_log ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    250    249            �           2604    121110    id    DEFAULT     r   ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);
 E   ALTER TABLE public.django_content_type ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    252    251            �           2604    121111    id    DEFAULT     x   ALTER TABLE ONLY django_cron_cronjoblog ALTER COLUMN id SET DEFAULT nextval('django_cron_cronjoblog_id_seq'::regclass);
 H   ALTER TABLE public.django_cron_cronjoblog ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    254    253            �           2604    121112    id    DEFAULT     n   ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);
 C   ALTER TABLE public.django_migrations ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    256    255            �           2604    121113    id    DEFAULT     b   ALTER TABLE ONLY django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);
 =   ALTER TABLE public.django_site ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    259    258            �           2604    121114    id    DEFAULT     t   ALTER TABLE ONLY formazione_aspirante ALTER COLUMN id SET DEFAULT nextval('formazione_aspirante_id_seq'::regclass);
 F   ALTER TABLE public.formazione_aspirante ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    261    260            �           2604    121115    id    DEFAULT     �   ALTER TABLE ONLY formazione_assenzacorsobase ALTER COLUMN id SET DEFAULT nextval('formazione_assenzacorsobase_id_seq'::regclass);
 M   ALTER TABLE public.formazione_assenzacorsobase ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    263    262            �           2604    121116    id    DEFAULT     t   ALTER TABLE ONLY formazione_corsobase ALTER COLUMN id SET DEFAULT nextval('formazione_corsobase_id_seq'::regclass);
 F   ALTER TABLE public.formazione_corsobase ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    265    264            �           2604    121117    id    DEFAULT     �   ALTER TABLE ONLY formazione_lezionecorsobase ALTER COLUMN id SET DEFAULT nextval('formazione_lezionecorsobase_id_seq'::regclass);
 M   ALTER TABLE public.formazione_lezionecorsobase ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    267    266            �           2604    121118    id    DEFAULT     �   ALTER TABLE ONLY formazione_partecipazionecorsobase ALTER COLUMN id SET DEFAULT nextval('formazione_partecipazionecorsobase_id_seq'::regclass);
 T   ALTER TABLE public.formazione_partecipazionecorsobase ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    269    268            �           2604    121119    id    DEFAULT     r   ALTER TABLE ONLY gruppi_appartenenza ALTER COLUMN id SET DEFAULT nextval('gruppi_appartenenza_id_seq'::regclass);
 E   ALTER TABLE public.gruppi_appartenenza ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    271    270            �           2604    121120    id    DEFAULT     f   ALTER TABLE ONLY gruppi_gruppo ALTER COLUMN id SET DEFAULT nextval('gruppi_gruppo_id_seq'::regclass);
 ?   ALTER TABLE public.gruppi_gruppo ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    273    272            �           2604    121121    id    DEFAULT     l   ALTER TABLE ONLY patenti_elemento ALTER COLUMN id SET DEFAULT nextval('patenti_elemento_id_seq'::regclass);
 B   ALTER TABLE public.patenti_elemento ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    275    274            �           2604    121122    id    DEFAULT     j   ALTER TABLE ONLY patenti_patente ALTER COLUMN id SET DEFAULT nextval('patenti_patente_id_seq'::regclass);
 A   ALTER TABLE public.patenti_patente ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    277    276            �           2604    121123    id    DEFAULT     p   ALTER TABLE ONLY posta_destinatario ALTER COLUMN id SET DEFAULT nextval('posta_destinatario_id_seq'::regclass);
 D   ALTER TABLE public.posta_destinatario ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    279    278            �           2604    121124    id    DEFAULT     j   ALTER TABLE ONLY posta_messaggio ALTER COLUMN id SET DEFAULT nextval('posta_messaggio_id_seq'::regclass);
 A   ALTER TABLE public.posta_messaggio ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    281    280            �           2604    121125    id    DEFAULT     j   ALTER TABLE ONLY sangue_donatore ALTER COLUMN id SET DEFAULT nextval('sangue_donatore_id_seq'::regclass);
 A   ALTER TABLE public.sangue_donatore ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    283    282                        2604    121126    id    DEFAULT     l   ALTER TABLE ONLY sangue_donazione ALTER COLUMN id SET DEFAULT nextval('sangue_donazione_id_seq'::regclass);
 B   ALTER TABLE public.sangue_donazione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    285    284                       2604    121127    id    DEFAULT     f   ALTER TABLE ONLY sangue_merito ALTER COLUMN id SET DEFAULT nextval('sangue_merito_id_seq'::regclass);
 ?   ALTER TABLE public.sangue_merito ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    287    286                       2604    121128    id    DEFAULT     b   ALTER TABLE ONLY sangue_sede ALTER COLUMN id SET DEFAULT nextval('sangue_sede_id_seq'::regclass);
 =   ALTER TABLE public.sangue_sede ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    289    288                       2604    121129    id    DEFAULT     j   ALTER TABLE ONLY social_commento ALTER COLUMN id SET DEFAULT nextval('social_commento_id_seq'::regclass);
 A   ALTER TABLE public.social_commento ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    291    290                       2604    121130    id    DEFAULT     j   ALTER TABLE ONLY social_giudizio ALTER COLUMN id SET DEFAULT nextval('social_giudizio_id_seq'::regclass);
 A   ALTER TABLE public.social_giudizio ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    293    292                       2604    121131    id    DEFAULT     p   ALTER TABLE ONLY ufficio_soci_quota ALTER COLUMN id SET DEFAULT nextval('ufficio_soci_quota_id_seq'::regclass);
 D   ALTER TABLE public.ufficio_soci_quota ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    296    295                       2604    121132    id    DEFAULT     ~   ALTER TABLE ONLY ufficio_soci_tesseramento ALTER COLUMN id SET DEFAULT nextval('ufficio_soci_tesseramento_id_seq'::regclass);
 K   ALTER TABLE public.ufficio_soci_tesseramento ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    298    297            	           2604    121133    id    DEFAULT     x   ALTER TABLE ONLY ufficio_soci_tesserino ALTER COLUMN id SET DEFAULT nextval('ufficio_soci_tesserino_id_seq'::regclass);
 H   ALTER TABLE public.ufficio_soci_tesserino ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    300    299            
           2604    121134    id    DEFAULT     n   ALTER TABLE ONLY veicoli_autoparco ALTER COLUMN id SET DEFAULT nextval('veicoli_autoparco_id_seq'::regclass);
 C   ALTER TABLE public.veicoli_autoparco ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    302    301                       2604    121135    id    DEFAULT     t   ALTER TABLE ONLY veicoli_collocazione ALTER COLUMN id SET DEFAULT nextval('veicoli_collocazione_id_seq'::regclass);
 F   ALTER TABLE public.veicoli_collocazione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    304    303                       2604    121136    id    DEFAULT     t   ALTER TABLE ONLY veicoli_fermotecnico ALTER COLUMN id SET DEFAULT nextval('veicoli_fermotecnico_id_seq'::regclass);
 F   ALTER TABLE public.veicoli_fermotecnico ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    306    305                       2604    121137    id    DEFAULT     t   ALTER TABLE ONLY veicoli_manutenzione ALTER COLUMN id SET DEFAULT nextval('veicoli_manutenzione_id_seq'::regclass);
 F   ALTER TABLE public.veicoli_manutenzione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    308    307                       2604    121138    id    DEFAULT     t   ALTER TABLE ONLY veicoli_rifornimento ALTER COLUMN id SET DEFAULT nextval('veicoli_rifornimento_id_seq'::regclass);
 F   ALTER TABLE public.veicoli_rifornimento ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    310    309                       2604    121139    id    DEFAULT     t   ALTER TABLE ONLY veicoli_segnalazione ALTER COLUMN id SET DEFAULT nextval('veicoli_segnalazione_id_seq'::regclass);
 F   ALTER TABLE public.veicoli_segnalazione ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    312    311                       2604    121140    id    DEFAULT     j   ALTER TABLE ONLY veicoli_veicolo ALTER COLUMN id SET DEFAULT nextval('veicoli_veicolo_id_seq'::regclass);
 A   ALTER TABLE public.veicoli_veicolo ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    314    313            �          0    120651    anagrafica_appartenenza 
   TABLE DATA               �   COPY anagrafica_appartenenza (id, creazione, ultima_modifica, inizio, fine, confermata, ritirata, membro, terminazione, persona_id, precedente_id, sede_id, vecchia_sede_id) FROM stdin;
    public       postgres    false    187   '�      a           0    0    anagrafica_appartenenza_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('anagrafica_appartenenza_id_seq', 30, true);
            public       postgres    false    188            �          0    120656    anagrafica_delega 
   TABLE DATA               �   COPY anagrafica_delega (id, creazione, ultima_modifica, inizio, fine, tipo, oggetto_id, firmatario_id, oggetto_tipo_id, persona_id) FROM stdin;
    public       postgres    false    189   D�      b           0    0    anagrafica_delega_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('anagrafica_delega_id_seq', 17, true);
            public       postgres    false    190            �          0    120662    anagrafica_dimissione 
   TABLE DATA               �   COPY anagrafica_dimissione (id, motivo, info, appartenenza_id, persona_id, richiedente_id, sede_id, creazione, ultima_modifica) FROM stdin;
    public       postgres    false    191   a�      c           0    0    anagrafica_dimissione_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('anagrafica_dimissione_id_seq', 1, false);
            public       postgres    false    192            �          0    120670    anagrafica_documento 
   TABLE DATA               _   COPY anagrafica_documento (id, creazione, ultima_modifica, tipo, file, persona_id) FROM stdin;
    public       postgres    false    193   ~�      d           0    0    anagrafica_documento_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('anagrafica_documento_id_seq', 1, true);
            public       postgres    false    194            �          0    120675    anagrafica_estensione 
   TABLE DATA               �   COPY anagrafica_estensione (id, creazione, ultima_modifica, confermata, ritirata, protocollo_numero, protocollo_data, motivo, appartenenza_id, destinazione_id, persona_id, richiedente_id) FROM stdin;
    public       postgres    false    195   ��      e           0    0    anagrafica_estensione_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('anagrafica_estensione_id_seq', 2, true);
            public       postgres    false    196            �          0    120683    anagrafica_fototessera 
   TABLE DATA               q   COPY anagrafica_fototessera (id, creazione, ultima_modifica, confermata, ritirata, file, persona_id) FROM stdin;
    public       postgres    false    197   ��      f           0    0    anagrafica_fototessera_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('anagrafica_fototessera_id_seq', 1, false);
            public       postgres    false    198            �          0    120688    anagrafica_persona 
   TABLE DATA               �  COPY anagrafica_persona (id, creazione, ultima_modifica, vecchio_id, nome, cognome, codice_fiscale, data_nascita, genere, stato, comune_nascita, provincia_nascita, stato_nascita, indirizzo_residenza, comune_residenza, provincia_residenza, stato_residenza, cap_residenza, email_contatto, note, avatar, privacy_contatti, privacy_curriculum, privacy_deleghe, cm, conoscenza, iv) FROM stdin;
    public       postgres    false    199   ��      g           0    0    anagrafica_persona_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('anagrafica_persona_id_seq', 38, true);
            public       postgres    false    200            �          0    120696 $   anagrafica_provvedimentodisciplinare 
   TABLE DATA               �   COPY anagrafica_provvedimentodisciplinare (id, creazione, ultima_modifica, protocollo_data, protocollo_numero, inizio, fine, motivazione, tipo, persona_id, sede_id, registrato_da_id) FROM stdin;
    public       postgres    false    201   ��      h           0    0 +   anagrafica_provvedimentodisciplinare_id_seq    SEQUENCE SET     S   SELECT pg_catalog.setval('anagrafica_provvedimentodisciplinare_id_seq', 1, false);
            public       postgres    false    202            �          0    120704    anagrafica_riserva 
   TABLE DATA               �   COPY anagrafica_riserva (id, creazione, ultima_modifica, inizio, fine, confermata, ritirata, appartenenza_id, motivo, persona_id, protocollo_data, protocollo_numero) FROM stdin;
    public       postgres    false    203   �      i           0    0    anagrafica_riserva_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('anagrafica_riserva_id_seq', 1, false);
            public       postgres    false    204            �          0    120712    anagrafica_sede 
   TABLE DATA               �   COPY anagrafica_sede (id, creazione, ultima_modifica, nome, vecchio_id, estensione, tipo, telefono, fax, email, codice_fiscale, partita_iva, attiva, slug, lft, rght, tree_id, level, genitore_id, locazione_id, pec, iban, sito_web) FROM stdin;
    public       postgres    false    205   ,�      j           0    0    anagrafica_sede_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('anagrafica_sede_id_seq', 45, true);
            public       postgres    false    206            �          0    120724    anagrafica_telefono 
   TABLE DATA               d   COPY anagrafica_telefono (id, creazione, ultima_modifica, numero, servizio, persona_id) FROM stdin;
    public       postgres    false    207   I�      k           0    0    anagrafica_telefono_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('anagrafica_telefono_id_seq', 1, false);
            public       postgres    false    208            �          0    120729    anagrafica_trasferimento 
   TABLE DATA               �   COPY anagrafica_trasferimento (id, creazione, ultima_modifica, confermata, ritirata, protocollo_numero, protocollo_data, motivo, appartenenza_id, destinazione_id, persona_id, richiedente_id) FROM stdin;
    public       postgres    false    209   f�      l           0    0    anagrafica_trasferimento_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('anagrafica_trasferimento_id_seq', 1, false);
            public       postgres    false    210            �          0    120737    attivita_area 
   TABLE DATA               Z   COPY attivita_area (id, creazione, ultima_modifica, nome, obiettivo, sede_id) FROM stdin;
    public       postgres    false    211   ��      m           0    0    attivita_area_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('attivita_area_id_seq', 4, true);
            public       postgres    false    212            �          0    120742    attivita_attivita 
   TABLE DATA               �   COPY attivita_attivita (id, creazione, ultima_modifica, vecchio_id, nome, stato, apertura, descrizione, area_id, estensione_id, locazione_id, sede_id, centrale_operativa) FROM stdin;
    public       postgres    false    213   ��      n           0    0    attivita_attivita_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('attivita_attivita_id_seq', 6, true);
            public       postgres    false    214            �          0    120750    attivita_partecipazione 
   TABLE DATA               �   COPY attivita_partecipazione (id, creazione, ultima_modifica, confermata, ritirata, stato, persona_id, turno_id, centrale_operativa) FROM stdin;
    public       postgres    false    215   ��      o           0    0    attivita_partecipazione_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('attivita_partecipazione_id_seq', 1, true);
            public       postgres    false    216            �          0    120755    attivita_turno 
   TABLE DATA               �   COPY attivita_turno (id, creazione, ultima_modifica, nome, prenotazione, inizio, fine, minimo, massimo, attivita_id) FROM stdin;
    public       postgres    false    217   ��      p           0    0    attivita_turno_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('attivita_turno_id_seq', 8, true);
            public       postgres    false    218            �          0    120760    autenticazione_utenza 
   TABLE DATA               �   COPY autenticazione_utenza (id, password, last_login, is_superuser, creazione, ultima_modifica, email, ultimo_accesso, ultimo_consenso, is_staff, is_active, persona_id) FROM stdin;
    public       postgres    false    219   ��      �          0    120763    autenticazione_utenza_groups 
   TABLE DATA               H   COPY autenticazione_utenza_groups (id, utenza_id, group_id) FROM stdin;
    public       postgres    false    220   �      q           0    0 #   autenticazione_utenza_groups_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('autenticazione_utenza_groups_id_seq', 1, false);
            public       postgres    false    221            r           0    0    autenticazione_utenza_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('autenticazione_utenza_id_seq', 1, true);
            public       postgres    false    222            �          0    120770 &   autenticazione_utenza_user_permissions 
   TABLE DATA               W   COPY autenticazione_utenza_user_permissions (id, utenza_id, permission_id) FROM stdin;
    public       postgres    false    223   1�      s           0    0 -   autenticazione_utenza_user_permissions_id_seq    SEQUENCE SET     U   SELECT pg_catalog.setval('autenticazione_utenza_user_permissions_id_seq', 1, false);
            public       postgres    false    224            �          0    120775 
   auth_group 
   TABLE DATA               '   COPY auth_group (id, name) FROM stdin;
    public       postgres    false    225   N�      t           0    0    auth_group_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('auth_group_id_seq', 1, false);
            public       postgres    false    226            �          0    120780    auth_group_permissions 
   TABLE DATA               F   COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
    public       postgres    false    227   k�      u           0    0    auth_group_permissions_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);
            public       postgres    false    228            �          0    120785    auth_permission 
   TABLE DATA               G   COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
    public       postgres    false    229   ��      v           0    0    auth_permission_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('auth_permission_id_seq', 390, true);
            public       postgres    false    230            �          0    120790    base_allegato 
   TABLE DATA               s   COPY base_allegato (id, creazione, ultima_modifica, oggetto_id, file, nome, oggetto_tipo_id, scadenza) FROM stdin;
    public       postgres    false    231   �      w           0    0    base_allegato_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('base_allegato_id_seq', 1, true);
            public       postgres    false    232            �          0    120796    base_autorizzazione 
   TABLE DATA                 COPY base_autorizzazione (id, creazione, ultima_modifica, concessa, motivo_negazione, oggetto_id, necessaria, progressivo, destinatario_ruolo, destinatario_oggetto_id, destinatario_oggetto_tipo_id, firmatario_id, oggetto_tipo_id, richiedente_id) FROM stdin;
    public       postgres    false    233   $�      x           0    0    base_autorizzazione_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('base_autorizzazione_id_seq', 5, true);
            public       postgres    false    234            �          0    120807    base_locazione 
   TABLE DATA               �   COPY base_locazione (id, creazione, ultima_modifica, indirizzo, geo, via, civico, comune, provincia, regione, cap, stato) FROM stdin;
    public       postgres    false    235   A�      y           0    0    base_locazione_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('base_locazione_id_seq', 1, false);
            public       postgres    false    236            �          0    120815    base_log 
   TABLE DATA               �   COPY base_log (id, creazione, ultima_modifica, azione, oggetto_repr, oggetto_app_label, oggetto_model, oggetto_pk, oggetto_campo, valore_precedente, valore_successivo, persona_id) FROM stdin;
    public       postgres    false    237   ^�      z           0    0    base_log_id_seq    SEQUENCE SET     7   SELECT pg_catalog.setval('base_log_id_seq', 1, false);
            public       postgres    false    238            �          0    120823 
   base_token 
   TABLE DATA               g   COPY base_token (id, creazione, ultima_modifica, codice, persona_id, redirect, valido_ore) FROM stdin;
    public       postgres    false    239   {�      {           0    0    base_token_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('base_token_id_seq', 1, false);
            public       postgres    false    240            �          0    120828    centrale_operativa_reperibilita 
   TABLE DATA               y   COPY centrale_operativa_reperibilita (id, creazione, ultima_modifica, inizio, fine, attivazione, persona_id) FROM stdin;
    public       postgres    false    241   ��      |           0    0 &   centrale_operativa_reperibilita_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('centrale_operativa_reperibilita_id_seq', 1, false);
            public       postgres    false    242            �          0    120833    centrale_operativa_turno 
   TABLE DATA               �   COPY centrale_operativa_turno (id, creazione, ultima_modifica, montato_data, smontato_data, montato_da_id, persona_id, smontato_da_id, turno_id) FROM stdin;
    public       postgres    false    243   ��      }           0    0    centrale_operativa_turno_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('centrale_operativa_turno_id_seq', 1, false);
            public       postgres    false    244            �          0    120838    curriculum_titolo 
   TABLE DATA               �   COPY curriculum_titolo (id, vecchio_id, tipo, richiede_conferma, richiede_data_ottenimento, richiede_luogo_ottenimento, richiede_data_scadenza, richiede_codice, inseribile_in_autonomia, nome) FROM stdin;
    public       postgres    false    245   ��      ~           0    0    curriculum_titolo_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('curriculum_titolo_id_seq', 1, false);
            public       postgres    false    246            �          0    120843    curriculum_titolopersonale 
   TABLE DATA               �   COPY curriculum_titolopersonale (id, creazione, ultima_modifica, confermata, ritirata, data_ottenimento, luogo_ottenimento, data_scadenza, codice, codice_corso, certificato, certificato_da_id, persona_id, titolo_id) FROM stdin;
    public       postgres    false    247   ��                 0    0 !   curriculum_titolopersonale_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('curriculum_titolopersonale_id_seq', 1, false);
            public       postgres    false    248            �          0    120851    django_admin_log 
   TABLE DATA               �   COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
    public       postgres    false    249   �      �           0    0    django_admin_log_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);
            public       postgres    false    250            �          0    120860    django_content_type 
   TABLE DATA               <   COPY django_content_type (id, app_label, model) FROM stdin;
    public       postgres    false    251   )�      �           0    0    django_content_type_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('django_content_type_id_seq', 130, true);
            public       postgres    false    252            �          0    120865    django_cron_cronjoblog 
   TABLE DATA               k   COPY django_cron_cronjoblog (id, code, start_time, end_time, is_success, message, ran_at_time) FROM stdin;
    public       postgres    false    253   ��      �           0    0    django_cron_cronjoblog_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('django_cron_cronjoblog_id_seq', 1, false);
            public       postgres    false    254            �          0    120873    django_migrations 
   TABLE DATA               <   COPY django_migrations (id, app, name, applied) FROM stdin;
    public       postgres    false    255   ��      �           0    0    django_migrations_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('django_migrations_id_seq', 134, true);
            public       postgres    false    256            �          0    120881    django_session 
   TABLE DATA               I   COPY django_session (session_key, session_data, expire_date) FROM stdin;
    public       postgres    false    257   ��      �          0    120887    django_site 
   TABLE DATA               0   COPY django_site (id, domain, name) FROM stdin;
    public       postgres    false    258   ��      �           0    0    django_site_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('django_site_id_seq', 1, true);
            public       postgres    false    259            �          0    120892    formazione_aspirante 
   TABLE DATA               i   COPY formazione_aspirante (id, creazione, ultima_modifica, raggio, locazione_id, persona_id) FROM stdin;
    public       postgres    false    260   %�      �           0    0    formazione_aspirante_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('formazione_aspirante_id_seq', 1, false);
            public       postgres    false    261            �          0    120897    formazione_assenzacorsobase 
   TABLE DATA               x   COPY formazione_assenzacorsobase (id, creazione, ultima_modifica, lezione_id, persona_id, registrata_da_id) FROM stdin;
    public       postgres    false    262   B�      �           0    0 "   formazione_assenzacorsobase_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('formazione_assenzacorsobase_id_seq', 1, false);
            public       postgres    false    263            �          0    120902    formazione_corsobase 
   TABLE DATA               �   COPY formazione_corsobase (id, creazione, ultima_modifica, stato, data_inizio, data_esame, progressivo, anno, descrizione, locazione_id, sede_id, vecchio_id, data_attivazione, data_convocazione, op_attivazione, op_convocazione) FROM stdin;
    public       postgres    false    264   _�      �           0    0    formazione_corsobase_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('formazione_corsobase_id_seq', 1, false);
            public       postgres    false    265            �          0    120910    formazione_lezionecorsobase 
   TABLE DATA               l   COPY formazione_lezionecorsobase (id, creazione, ultima_modifica, inizio, fine, nome, corso_id) FROM stdin;
    public       postgres    false    266   |�      �           0    0 "   formazione_lezionecorsobase_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('formazione_lezionecorsobase_id_seq', 1, false);
            public       postgres    false    267            �          0    120915 "   formazione_partecipazionecorsobase 
   TABLE DATA                 COPY formazione_partecipazionecorsobase (id, creazione, ultima_modifica, confermata, ritirata, esito_esame, ammissione, motivo_non_ammissione, esito_parte_1, argomento_parte_1, esito_parte_2, argomento_parte_2, extra_1, extra_2, corso_id, persona_id, destinazione_id) FROM stdin;
    public       postgres    false    268   ��      �           0    0 )   formazione_partecipazionecorsobase_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('formazione_partecipazionecorsobase_id_seq', 1, false);
            public       postgres    false    269            �          0    120923    gruppi_appartenenza 
   TABLE DATA               �   COPY gruppi_appartenenza (id, creazione, ultima_modifica, inizio, fine, motivo_negazione, gruppo_id, negato_da_id, persona_id) FROM stdin;
    public       postgres    false    270   ��      �           0    0    gruppi_appartenenza_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('gruppi_appartenenza_id_seq', 1, false);
            public       postgres    false    271            �          0    120931    gruppi_gruppo 
   TABLE DATA               |   COPY gruppi_gruppo (id, creazione, ultima_modifica, estensione, nome, obiettivo, area_id, attivita_id, sede_id) FROM stdin;
    public       postgres    false    272   ��      �           0    0    gruppi_gruppo_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('gruppi_gruppo_id_seq', 1, false);
            public       postgres    false    273            �          0    120936    patenti_elemento 
   TABLE DATA               Y   COPY patenti_elemento (id, creazione, ultima_modifica, confermata, ritirata) FROM stdin;
    public       postgres    false    274   ��      �           0    0    patenti_elemento_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('patenti_elemento_id_seq', 1, false);
            public       postgres    false    275            �          0    120941    patenti_patente 
   TABLE DATA               H   COPY patenti_patente (id, creazione, ultima_modifica, tipo) FROM stdin;
    public       postgres    false    276   �      �           0    0    patenti_patente_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('patenti_patente_id_seq', 1, false);
            public       postgres    false    277            �          0    120946    posta_destinatario 
   TABLE DATA               {   COPY posta_destinatario (id, creazione, ultima_modifica, inviato, tentativo, errore, messaggio_id, persona_id) FROM stdin;
    public       postgres    false    278   *�      �           0    0    posta_destinatario_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('posta_destinatario_id_seq', 7, true);
            public       postgres    false    279            �          0    120951    posta_messaggio 
   TABLE DATA               �   COPY posta_messaggio (id, creazione, ultima_modifica, oggetto, corpo, ultimo_tentativo, terminato, mittente_id, rispondi_a_id) FROM stdin;
    public       postgres    false    280   G�      �           0    0    posta_messaggio_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('posta_messaggio_id_seq', 7, true);
            public       postgres    false    281            �          0    120959    sangue_donatore 
   TABLE DATA               �   COPY sangue_donatore (id, creazione, ultima_modifica, gruppo_sanguigno, fattore_rh, fanotipo_rh, kell, codice_sit, persona_id, sede_sit_id) FROM stdin;
    public       postgres    false    282   d�      �           0    0    sangue_donatore_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('sangue_donatore_id_seq', 1, false);
            public       postgres    false    283            �          0    120964    sangue_donazione 
   TABLE DATA               z   COPY sangue_donazione (id, creazione, ultima_modifica, confermata, ritirata, tipo, data, persona_id, sede_id) FROM stdin;
    public       postgres    false    284   ��      �           0    0    sangue_donazione_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('sangue_donazione_id_seq', 1, false);
            public       postgres    false    285            �          0    120969    sangue_merito 
   TABLE DATA               _   COPY sangue_merito (id, creazione, ultima_modifica, donazione, merito, persona_id) FROM stdin;
    public       postgres    false    286   ��      �           0    0    sangue_merito_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('sangue_merito_id_seq', 1, false);
            public       postgres    false    287            �          0    120974    sangue_sede 
   TABLE DATA               C   COPY sangue_sede (id, citta, provincia, regione, nome) FROM stdin;
    public       postgres    false    288   ��      �           0    0    sangue_sede_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('sangue_sede_id_seq', 1, false);
            public       postgres    false    289                       0    120979    social_commento 
   TABLE DATA               t   COPY social_commento (id, creazione, ultima_modifica, commento, oggetto_id, autore_id, oggetto_tipo_id) FROM stdin;
    public       postgres    false    290   ��      �           0    0    social_commento_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('social_commento_id_seq', 1, false);
            public       postgres    false    291                      0    120988    social_giudizio 
   TABLE DATA               t   COPY social_giudizio (id, creazione, ultima_modifica, positivo, oggetto_id, autore_id, oggetto_tipo_id) FROM stdin;
    public       postgres    false    292   ��      �           0    0    social_giudizio_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('social_giudizio_id_seq', 1, false);
            public       postgres    false    293            �          0    119632    spatial_ref_sys 
   TABLE DATA               "   COPY spatial_ref_sys  FROM stdin;
    public       postgres    false    175   �                0    120994    thumbnail_kvstore 
   TABLE DATA               0   COPY thumbnail_kvstore (key, value) FROM stdin;
    public       postgres    false    294   /�                0    121000    ufficio_soci_quota 
   TABLE DATA                 COPY ufficio_soci_quota (id, creazione, ultima_modifica, progressivo, anno, data_versamento, data_annullamento, stato, tipo, importo, importo_extra, causale, causale_extra, annullato_da_id, appartenenza_id, persona_id, registrato_da_id, sede_id, vecchio_id) FROM stdin;
    public       postgres    false    295   L�      �           0    0    ufficio_soci_quota_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('ufficio_soci_quota_id_seq', 1, false);
            public       postgres    false    296                      0    121008    ufficio_soci_tesseramento 
   TABLE DATA               �   COPY ufficio_soci_tesseramento (id, creazione, ultima_modifica, stato, anno, inizio, quota_attivo, quota_ordinario, quota_benemerito, quota_aspirante, quota_sostenitore) FROM stdin;
    public       postgres    false    297   i�      �           0    0     ufficio_soci_tesseramento_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('ufficio_soci_tesseramento_id_seq', 1, false);
            public       postgres    false    298            	          0    121013    ufficio_soci_tesserino 
   TABLE DATA                 COPY ufficio_soci_tesserino (id, creazione, ultima_modifica, tipo_richiesta, stato_richiesta, motivo_richiesta, motivo_rifiutato, stato_emissione, valido, codice, data_conferma, data_riconsegna, confermato_da_id, emesso_da_id, persona_id, richiesto_da_id, riconsegnato_a_id) FROM stdin;
    public       postgres    false    299   ��      �           0    0    ufficio_soci_tesserino_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('ufficio_soci_tesserino_id_seq', 1, false);
            public       postgres    false    300                      0    121021    veicoli_autoparco 
   TABLE DATA               w   COPY veicoli_autoparco (id, creazione, ultima_modifica, estensione, nome, telefono, locazione_id, sede_id) FROM stdin;
    public       postgres    false    301   ��      �           0    0    veicoli_autoparco_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('veicoli_autoparco_id_seq', 1, false);
            public       postgres    false    302                      0    121026    veicoli_collocazione 
   TABLE DATA               }   COPY veicoli_collocazione (id, creazione, ultima_modifica, inizio, fine, autoparco_id, creato_da_id, veicolo_id) FROM stdin;
    public       postgres    false    303   ��      �           0    0    veicoli_collocazione_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('veicoli_collocazione_id_seq', 1, false);
            public       postgres    false    304                      0    121031    veicoli_fermotecnico 
   TABLE DATA               w   COPY veicoli_fermotecnico (id, creazione, ultima_modifica, inizio, fine, motivo, creato_da_id, veicolo_id) FROM stdin;
    public       postgres    false    305   ��      �           0    0    veicoli_fermotecnico_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('veicoli_fermotecnico_id_seq', 1, false);
            public       postgres    false    306                      0    121039    veicoli_manutenzione 
   TABLE DATA               �   COPY veicoli_manutenzione (id, creazione, ultima_modifica, tipo, data, descrizione, km, manutentore, numero_fattura, costo, creato_da_id, veicolo_id) FROM stdin;
    public       postgres    false    307   ��      �           0    0    veicoli_manutenzione_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('veicoli_manutenzione_id_seq', 1, false);
            public       postgres    false    308                      0    121048    veicoli_rifornimento 
   TABLE DATA               �   COPY veicoli_rifornimento (id, creazione, ultima_modifica, data, contachilometri, costo, consumo_carburante, presso, contalitri, ricevuta, veicolo_id, creato_da_id) FROM stdin;
    public       postgres    false    309   �      �           0    0    veicoli_rifornimento_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('veicoli_rifornimento_id_seq', 1, false);
            public       postgres    false    310                      0    121054    veicoli_segnalazione 
   TABLE DATA               |   COPY veicoli_segnalazione (id, creazione, ultima_modifica, descrizione, autore_id, manutenzione_id, veicolo_id) FROM stdin;
    public       postgres    false    311   4�      �           0    0    veicoli_segnalazione_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('veicoli_segnalazione_id_seq', 1, false);
            public       postgres    false    312                      0    121062    veicoli_veicolo 
   TABLE DATA               K  COPY veicoli_veicolo (id, creazione, ultima_modifica, stato, libretto, targa, prima_immatricolazione, proprietario_cognome, proprietario_nome, proprietario_indirizzo, pneumatici_anteriori, pneumatici_posteriori, pneumatici_alt_anteriori, pneumatici_alt_posteriori, cambio, lunghezza, larghezza, sbalzo, tara, marca, modello, telaio, massa_max, data_immatricolazione, categoria, destinazione, carrozzeria, omologazione, num_assi, rimorchio_frenato, cilindrata, potenza_massima, alimentazione, posti, regime, card_rifornimento, selettiva_radio, telepass, intervallo_revisione) FROM stdin;
    public       postgres    false    313   Q�      �           0    0    veicoli_veicolo_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('veicoli_veicolo_id_seq', 1, false);
            public       postgres    false    314            4           2606    121142    anagrafica_appartenenza_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY anagrafica_appartenenza
    ADD CONSTRAINT anagrafica_appartenenza_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.anagrafica_appartenenza DROP CONSTRAINT anagrafica_appartenenza_pkey;
       public         postgres    false    187    187            K           2606    121144    anagrafica_delega_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY anagrafica_delega
    ADD CONSTRAINT anagrafica_delega_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.anagrafica_delega DROP CONSTRAINT anagrafica_delega_pkey;
       public         postgres    false    189    189            U           2606    121146    anagrafica_dimissione_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY anagrafica_dimissione
    ADD CONSTRAINT anagrafica_dimissione_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.anagrafica_dimissione DROP CONSTRAINT anagrafica_dimissione_pkey;
       public         postgres    false    191    191            [           2606    121148    anagrafica_documento_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY anagrafica_documento
    ADD CONSTRAINT anagrafica_documento_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.anagrafica_documento DROP CONSTRAINT anagrafica_documento_pkey;
       public         postgres    false    193    193            f           2606    121150    anagrafica_estensione_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY anagrafica_estensione
    ADD CONSTRAINT anagrafica_estensione_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.anagrafica_estensione DROP CONSTRAINT anagrafica_estensione_pkey;
       public         postgres    false    195    195            m           2606    121152    anagrafica_fototessera_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY anagrafica_fototessera
    ADD CONSTRAINT anagrafica_fototessera_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.anagrafica_fototessera DROP CONSTRAINT anagrafica_fototessera_pkey;
       public         postgres    false    197    197            x           2606    121154 %   anagrafica_persona_codice_fiscale_key 
   CONSTRAINT     v   ALTER TABLE ONLY anagrafica_persona
    ADD CONSTRAINT anagrafica_persona_codice_fiscale_key UNIQUE (codice_fiscale);
 b   ALTER TABLE ONLY public.anagrafica_persona DROP CONSTRAINT anagrafica_persona_codice_fiscale_key;
       public         postgres    false    199    199            �           2606    121156    anagrafica_persona_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY anagrafica_persona
    ADD CONSTRAINT anagrafica_persona_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.anagrafica_persona DROP CONSTRAINT anagrafica_persona_pkey;
       public         postgres    false    199    199            �           2606    121158 )   anagrafica_provvedimentodisciplinare_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY anagrafica_provvedimentodisciplinare
    ADD CONSTRAINT anagrafica_provvedimentodisciplinare_pkey PRIMARY KEY (id);
 x   ALTER TABLE ONLY public.anagrafica_provvedimentodisciplinare DROP CONSTRAINT anagrafica_provvedimentodisciplinare_pkey;
       public         postgres    false    201    201            �           2606    121160    anagrafica_riserva_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY anagrafica_riserva
    ADD CONSTRAINT anagrafica_riserva_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.anagrafica_riserva DROP CONSTRAINT anagrafica_riserva_pkey;
       public         postgres    false    203    203            �           2606    121162    anagrafica_sede_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY anagrafica_sede
    ADD CONSTRAINT anagrafica_sede_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.anagrafica_sede DROP CONSTRAINT anagrafica_sede_pkey;
       public         postgres    false    205    205            �           2606    121164    anagrafica_telefono_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY anagrafica_telefono
    ADD CONSTRAINT anagrafica_telefono_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.anagrafica_telefono DROP CONSTRAINT anagrafica_telefono_pkey;
       public         postgres    false    207    207            �           2606    121166    anagrafica_trasferimento_pkey 
   CONSTRAINT     m   ALTER TABLE ONLY anagrafica_trasferimento
    ADD CONSTRAINT anagrafica_trasferimento_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.anagrafica_trasferimento DROP CONSTRAINT anagrafica_trasferimento_pkey;
       public         postgres    false    209    209            �           2606    121168    attivita_area_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY attivita_area
    ADD CONSTRAINT attivita_area_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.attivita_area DROP CONSTRAINT attivita_area_pkey;
       public         postgres    false    211    211            �           2606    121170    attivita_attivita_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY attivita_attivita
    ADD CONSTRAINT attivita_attivita_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.attivita_attivita DROP CONSTRAINT attivita_attivita_pkey;
       public         postgres    false    213    213            �           2606    121172    attivita_partecipazione_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY attivita_partecipazione
    ADD CONSTRAINT attivita_partecipazione_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.attivita_partecipazione DROP CONSTRAINT attivita_partecipazione_pkey;
       public         postgres    false    215    215                       2606    121174    attivita_turno_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY attivita_turno
    ADD CONSTRAINT attivita_turno_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.attivita_turno DROP CONSTRAINT attivita_turno_pkey;
       public         postgres    false    217    217            
           2606    121176    autenticazione_utenza_email_key 
   CONSTRAINT     j   ALTER TABLE ONLY autenticazione_utenza
    ADD CONSTRAINT autenticazione_utenza_email_key UNIQUE (email);
 _   ALTER TABLE ONLY public.autenticazione_utenza DROP CONSTRAINT autenticazione_utenza_email_key;
       public         postgres    false    219    219                       2606    121178 !   autenticazione_utenza_groups_pkey 
   CONSTRAINT     u   ALTER TABLE ONLY autenticazione_utenza_groups
    ADD CONSTRAINT autenticazione_utenza_groups_pkey PRIMARY KEY (id);
 h   ALTER TABLE ONLY public.autenticazione_utenza_groups DROP CONSTRAINT autenticazione_utenza_groups_pkey;
       public         postgres    false    220    220                       2606    121180 4   autenticazione_utenza_groups_utenza_id_db0a7f00_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_groups
    ADD CONSTRAINT autenticazione_utenza_groups_utenza_id_db0a7f00_uniq UNIQUE (utenza_id, group_id);
 {   ALTER TABLE ONLY public.autenticazione_utenza_groups DROP CONSTRAINT autenticazione_utenza_groups_utenza_id_db0a7f00_uniq;
       public         postgres    false    220    220    220                       2606    121182 $   autenticazione_utenza_persona_id_key 
   CONSTRAINT     t   ALTER TABLE ONLY autenticazione_utenza
    ADD CONSTRAINT autenticazione_utenza_persona_id_key UNIQUE (persona_id);
 d   ALTER TABLE ONLY public.autenticazione_utenza DROP CONSTRAINT autenticazione_utenza_persona_id_key;
       public         postgres    false    219    219                       2606    121184    autenticazione_utenza_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY autenticazione_utenza
    ADD CONSTRAINT autenticazione_utenza_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.autenticazione_utenza DROP CONSTRAINT autenticazione_utenza_pkey;
       public         postgres    false    219    219                       2606    121186 +   autenticazione_utenza_user_permissions_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_user_permissions
    ADD CONSTRAINT autenticazione_utenza_user_permissions_pkey PRIMARY KEY (id);
 |   ALTER TABLE ONLY public.autenticazione_utenza_user_permissions DROP CONSTRAINT autenticazione_utenza_user_permissions_pkey;
       public         postgres    false    223    223                       2606    121188 >   autenticazione_utenza_user_permissions_utenza_id_c5ee131a_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_user_permissions
    ADD CONSTRAINT autenticazione_utenza_user_permissions_utenza_id_c5ee131a_uniq UNIQUE (utenza_id, permission_id);
 �   ALTER TABLE ONLY public.autenticazione_utenza_user_permissions DROP CONSTRAINT autenticazione_utenza_user_permissions_utenza_id_c5ee131a_uniq;
       public         postgres    false    223    223    223                       2606    121190    auth_group_name_key 
   CONSTRAINT     R   ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);
 H   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
       public         postgres    false    225    225            #           2606    121192 -   auth_group_permissions_group_id_0cd325b0_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_0cd325b0_uniq UNIQUE (group_id, permission_id);
 n   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_0cd325b0_uniq;
       public         postgres    false    227    227    227            %           2606    121194    auth_group_permissions_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
       public         postgres    false    227    227                       2606    121196    auth_group_pkey 
   CONSTRAINT     Q   ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
       public         postgres    false    225    225            (           2606    121198 -   auth_permission_content_type_id_01ab375a_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_01ab375a_uniq UNIQUE (content_type_id, codename);
 g   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_01ab375a_uniq;
       public         postgres    false    229    229    229            *           2606    121200    auth_permission_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
       public         postgres    false    229    229            1           2606    121202    base_allegato_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY base_allegato
    ADD CONSTRAINT base_allegato_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.base_allegato DROP CONSTRAINT base_allegato_pkey;
       public         postgres    false    231    231            F           2606    121204    base_autorizzazione_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY base_autorizzazione
    ADD CONSTRAINT base_autorizzazione_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.base_autorizzazione DROP CONSTRAINT base_autorizzazione_pkey;
       public         postgres    false    233    233            S           2606    121206    base_locazione_indirizzo_key 
   CONSTRAINT     d   ALTER TABLE ONLY base_locazione
    ADD CONSTRAINT base_locazione_indirizzo_key UNIQUE (indirizzo);
 U   ALTER TABLE ONLY public.base_locazione DROP CONSTRAINT base_locazione_indirizzo_key;
       public         postgres    false    235    235            U           2606    121208    base_locazione_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY base_locazione
    ADD CONSTRAINT base_locazione_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.base_locazione DROP CONSTRAINT base_locazione_pkey;
       public         postgres    false    235    235            c           2606    121210    base_log_pkey 
   CONSTRAINT     M   ALTER TABLE ONLY base_log
    ADD CONSTRAINT base_log_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.base_log DROP CONSTRAINT base_log_pkey;
       public         postgres    false    237    237            g           2606    121212    base_token_codice_key 
   CONSTRAINT     V   ALTER TABLE ONLY base_token
    ADD CONSTRAINT base_token_codice_key UNIQUE (codice);
 J   ALTER TABLE ONLY public.base_token DROP CONSTRAINT base_token_codice_key;
       public         postgres    false    239    239            k           2606    121214    base_token_pkey 
   CONSTRAINT     Q   ALTER TABLE ONLY base_token
    ADD CONSTRAINT base_token_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.base_token DROP CONSTRAINT base_token_pkey;
       public         postgres    false    239    239            r           2606    121216 $   centrale_operativa_reperibilita_pkey 
   CONSTRAINT     {   ALTER TABLE ONLY centrale_operativa_reperibilita
    ADD CONSTRAINT centrale_operativa_reperibilita_pkey PRIMARY KEY (id);
 n   ALTER TABLE ONLY public.centrale_operativa_reperibilita DROP CONSTRAINT centrale_operativa_reperibilita_pkey;
       public         postgres    false    241    241            {           2606    121218    centrale_operativa_turno_pkey 
   CONSTRAINT     m   ALTER TABLE ONLY centrale_operativa_turno
    ADD CONSTRAINT centrale_operativa_turno_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.centrale_operativa_turno DROP CONSTRAINT centrale_operativa_turno_pkey;
       public         postgres    false    243    243            �           2606    121220    curriculum_titolo_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY curriculum_titolo
    ADD CONSTRAINT curriculum_titolo_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.curriculum_titolo DROP CONSTRAINT curriculum_titolo_pkey;
       public         postgres    false    245    245            �           2606    121222    curriculum_titolopersonale_pkey 
   CONSTRAINT     q   ALTER TABLE ONLY curriculum_titolopersonale
    ADD CONSTRAINT curriculum_titolopersonale_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.curriculum_titolopersonale DROP CONSTRAINT curriculum_titolopersonale_pkey;
       public         postgres    false    247    247            �           2606    121224    django_admin_log_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
       public         postgres    false    249    249            �           2606    121226 +   django_content_type_app_label_76bd3d3b_uniq 
   CONSTRAINT        ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_76bd3d3b_uniq UNIQUE (app_label, model);
 i   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_76bd3d3b_uniq;
       public         postgres    false    251    251    251            �           2606    121228    django_content_type_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
       public         postgres    false    251    251            �           2606    121230    django_cron_cronjoblog_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY django_cron_cronjoblog
    ADD CONSTRAINT django_cron_cronjoblog_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.django_cron_cronjoblog DROP CONSTRAINT django_cron_cronjoblog_pkey;
       public         postgres    false    253    253            �           2606    121232    django_migrations_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.django_migrations DROP CONSTRAINT django_migrations_pkey;
       public         postgres    false    255    255            �           2606    121234    django_session_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
 L   ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
       public         postgres    false    257    257            �           2606    121236     django_site_domain_a2e37b91_uniq 
   CONSTRAINT     b   ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_domain_a2e37b91_uniq UNIQUE (domain);
 V   ALTER TABLE ONLY public.django_site DROP CONSTRAINT django_site_domain_a2e37b91_uniq;
       public         postgres    false    258    258            �           2606    121238    django_site_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.django_site DROP CONSTRAINT django_site_pkey;
       public         postgres    false    258    258            �           2606    121240 #   formazione_aspirante_persona_id_key 
   CONSTRAINT     r   ALTER TABLE ONLY formazione_aspirante
    ADD CONSTRAINT formazione_aspirante_persona_id_key UNIQUE (persona_id);
 b   ALTER TABLE ONLY public.formazione_aspirante DROP CONSTRAINT formazione_aspirante_persona_id_key;
       public         postgres    false    260    260            �           2606    121242    formazione_aspirante_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY formazione_aspirante
    ADD CONSTRAINT formazione_aspirante_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.formazione_aspirante DROP CONSTRAINT formazione_aspirante_pkey;
       public         postgres    false    260    260            �           2606    121244     formazione_assenzacorsobase_pkey 
   CONSTRAINT     s   ALTER TABLE ONLY formazione_assenzacorsobase
    ADD CONSTRAINT formazione_assenzacorsobase_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.formazione_assenzacorsobase DROP CONSTRAINT formazione_assenzacorsobase_pkey;
       public         postgres    false    262    262            �           2606    121246    formazione_corsobase_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY formazione_corsobase
    ADD CONSTRAINT formazione_corsobase_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.formazione_corsobase DROP CONSTRAINT formazione_corsobase_pkey;
       public         postgres    false    264    264            �           2606    121248     formazione_lezionecorsobase_pkey 
   CONSTRAINT     s   ALTER TABLE ONLY formazione_lezionecorsobase
    ADD CONSTRAINT formazione_lezionecorsobase_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.formazione_lezionecorsobase DROP CONSTRAINT formazione_lezionecorsobase_pkey;
       public         postgres    false    266    266            �           2606    121250 '   formazione_partecipazionecorsobase_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY formazione_partecipazionecorsobase
    ADD CONSTRAINT formazione_partecipazionecorsobase_pkey PRIMARY KEY (id);
 t   ALTER TABLE ONLY public.formazione_partecipazionecorsobase DROP CONSTRAINT formazione_partecipazionecorsobase_pkey;
       public         postgres    false    268    268            �           2606    121252    gruppi_appartenenza_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY gruppi_appartenenza
    ADD CONSTRAINT gruppi_appartenenza_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.gruppi_appartenenza DROP CONSTRAINT gruppi_appartenenza_pkey;
       public         postgres    false    270    270            �           2606    121254    gruppi_gruppo_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY gruppi_gruppo
    ADD CONSTRAINT gruppi_gruppo_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.gruppi_gruppo DROP CONSTRAINT gruppi_gruppo_pkey;
       public         postgres    false    272    272            �           2606    121256    patenti_elemento_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY patenti_elemento
    ADD CONSTRAINT patenti_elemento_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.patenti_elemento DROP CONSTRAINT patenti_elemento_pkey;
       public         postgres    false    274    274            �           2606    121258    patenti_patente_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY patenti_patente
    ADD CONSTRAINT patenti_patente_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.patenti_patente DROP CONSTRAINT patenti_patente_pkey;
       public         postgres    false    276    276                       2606    121260    posta_destinatario_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY posta_destinatario
    ADD CONSTRAINT posta_destinatario_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.posta_destinatario DROP CONSTRAINT posta_destinatario_pkey;
       public         postgres    false    278    278                       2606    121262    posta_messaggio_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY posta_messaggio
    ADD CONSTRAINT posta_messaggio_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.posta_messaggio DROP CONSTRAINT posta_messaggio_pkey;
       public         postgres    false    280    280                       2606    121264    sangue_donatore_persona_id_key 
   CONSTRAINT     h   ALTER TABLE ONLY sangue_donatore
    ADD CONSTRAINT sangue_donatore_persona_id_key UNIQUE (persona_id);
 X   ALTER TABLE ONLY public.sangue_donatore DROP CONSTRAINT sangue_donatore_persona_id_key;
       public         postgres    false    282    282                       2606    121266    sangue_donatore_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY sangue_donatore
    ADD CONSTRAINT sangue_donatore_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.sangue_donatore DROP CONSTRAINT sangue_donatore_pkey;
       public         postgres    false    282    282            #           2606    121268    sangue_donazione_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY sangue_donazione
    ADD CONSTRAINT sangue_donazione_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sangue_donazione DROP CONSTRAINT sangue_donazione_pkey;
       public         postgres    false    284    284            +           2606    121270    sangue_merito_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY sangue_merito
    ADD CONSTRAINT sangue_merito_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.sangue_merito DROP CONSTRAINT sangue_merito_pkey;
       public         postgres    false    286    286            -           2606    121272    sangue_sede_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY sangue_sede
    ADD CONSTRAINT sangue_sede_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.sangue_sede DROP CONSTRAINT sangue_sede_pkey;
       public         postgres    false    288    288            4           2606    121274    social_commento_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY social_commento
    ADD CONSTRAINT social_commento_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.social_commento DROP CONSTRAINT social_commento_pkey;
       public         postgres    false    290    290            <           2606    121276    social_giudizio_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY social_giudizio
    ADD CONSTRAINT social_giudizio_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.social_giudizio DROP CONSTRAINT social_giudizio_pkey;
       public         postgres    false    292    292            ?           2606    121278    thumbnail_kvstore_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY thumbnail_kvstore
    ADD CONSTRAINT thumbnail_kvstore_pkey PRIMARY KEY (key);
 R   ALTER TABLE ONLY public.thumbnail_kvstore DROP CONSTRAINT thumbnail_kvstore_pkey;
       public         postgres    false    294    294            L           2606    121280    ufficio_soci_quota_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio_soci_quota_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio_soci_quota_pkey;
       public         postgres    false    295    295            N           2606    121282 ,   ufficio_soci_quota_progressivo_4dd12648_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio_soci_quota_progressivo_4dd12648_uniq UNIQUE (progressivo, anno, sede_id);
 i   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio_soci_quota_progressivo_4dd12648_uniq;
       public         postgres    false    295    295    295    295            T           2606    121284 "   ufficio_soci_tesseramento_anno_key 
   CONSTRAINT     p   ALTER TABLE ONLY ufficio_soci_tesseramento
    ADD CONSTRAINT ufficio_soci_tesseramento_anno_key UNIQUE (anno);
 f   ALTER TABLE ONLY public.ufficio_soci_tesseramento DROP CONSTRAINT ufficio_soci_tesseramento_anno_key;
       public         postgres    false    297    297            V           2606    121286    ufficio_soci_tesseramento_pkey 
   CONSTRAINT     o   ALTER TABLE ONLY ufficio_soci_tesseramento
    ADD CONSTRAINT ufficio_soci_tesseramento_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.ufficio_soci_tesseramento DROP CONSTRAINT ufficio_soci_tesseramento_pkey;
       public         postgres    false    297    297            d           2606    121288 !   ufficio_soci_tesserino_codice_key 
   CONSTRAINT     n   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soci_tesserino_codice_key UNIQUE (codice);
 b   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soci_tesserino_codice_key;
       public         postgres    false    299    299            g           2606    121290    ufficio_soci_tesserino_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soci_tesserino_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soci_tesserino_pkey;
       public         postgres    false    299    299            s           2606    121292    veicoli_autoparco_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY veicoli_autoparco
    ADD CONSTRAINT veicoli_autoparco_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.veicoli_autoparco DROP CONSTRAINT veicoli_autoparco_pkey;
       public         postgres    false    301    301            |           2606    121294    veicoli_collocazione_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY veicoli_collocazione
    ADD CONSTRAINT veicoli_collocazione_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.veicoli_collocazione DROP CONSTRAINT veicoli_collocazione_pkey;
       public         postgres    false    303    303            �           2606    121296    veicoli_fermotecnico_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY veicoli_fermotecnico
    ADD CONSTRAINT veicoli_fermotecnico_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.veicoli_fermotecnico DROP CONSTRAINT veicoli_fermotecnico_pkey;
       public         postgres    false    305    305            �           2606    121298    veicoli_manutenzione_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY veicoli_manutenzione
    ADD CONSTRAINT veicoli_manutenzione_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.veicoli_manutenzione DROP CONSTRAINT veicoli_manutenzione_pkey;
       public         postgres    false    307    307            �           2606    121300    veicoli_rifornimento_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY veicoli_rifornimento
    ADD CONSTRAINT veicoli_rifornimento_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.veicoli_rifornimento DROP CONSTRAINT veicoli_rifornimento_pkey;
       public         postgres    false    309    309            �           2606    121302    veicoli_segnalazione_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY veicoli_segnalazione
    ADD CONSTRAINT veicoli_segnalazione_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.veicoli_segnalazione DROP CONSTRAINT veicoli_segnalazione_pkey;
       public         postgres    false    311    311            �           2606    121304    veicoli_veicolo_pkey 
   CONSTRAINT     [   ALTER TABLE ONLY veicoli_veicolo
    ADD CONSTRAINT veicoli_veicolo_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.veicoli_veicolo DROP CONSTRAINT veicoli_veicolo_pkey;
       public         postgres    false    313    313            �           2606    121306    veicoli_veicolo_telaio_key 
   CONSTRAINT     `   ALTER TABLE ONLY veicoli_veicolo
    ADD CONSTRAINT veicoli_veicolo_telaio_key UNIQUE (telaio);
 T   ALTER TABLE ONLY public.veicoli_veicolo DROP CONSTRAINT veicoli_veicolo_telaio_key;
       public         postgres    false    313    313                       1259    121307     anagrafica_appartenenza_0526208f    INDEX     h   CREATE INDEX anagrafica_appartenenza_0526208f ON anagrafica_appartenenza USING btree (vecchia_sede_id);
 4   DROP INDEX public.anagrafica_appartenenza_0526208f;
       public         postgres    false    187                       1259    121308     anagrafica_appartenenza_0687f864    INDEX     `   CREATE INDEX anagrafica_appartenenza_0687f864 ON anagrafica_appartenenza USING btree (sede_id);
 4   DROP INDEX public.anagrafica_appartenenza_0687f864;
       public         postgres    false    187                       1259    121309     anagrafica_appartenenza_3554fea7    INDEX     f   CREATE INDEX anagrafica_appartenenza_3554fea7 ON anagrafica_appartenenza USING btree (precedente_id);
 4   DROP INDEX public.anagrafica_appartenenza_3554fea7;
       public         postgres    false    187                       1259    121310     anagrafica_appartenenza_36063dc9    INDEX     b   CREATE INDEX anagrafica_appartenenza_36063dc9 ON anagrafica_appartenenza USING btree (creazione);
 4   DROP INDEX public.anagrafica_appartenenza_36063dc9;
       public         postgres    false    187                       1259    121311     anagrafica_appartenenza_43662d06    INDEX     c   CREATE INDEX anagrafica_appartenenza_43662d06 ON anagrafica_appartenenza USING btree (confermata);
 4   DROP INDEX public.anagrafica_appartenenza_43662d06;
       public         postgres    false    187                        1259    121312     anagrafica_appartenenza_4a9487af    INDEX     a   CREATE INDEX anagrafica_appartenenza_4a9487af ON anagrafica_appartenenza USING btree (ritirata);
 4   DROP INDEX public.anagrafica_appartenenza_4a9487af;
       public         postgres    false    187            !           1259    121313     anagrafica_appartenenza_69bd2e5f    INDEX     h   CREATE INDEX anagrafica_appartenenza_69bd2e5f ON anagrafica_appartenenza USING btree (ultima_modifica);
 4   DROP INDEX public.anagrafica_appartenenza_69bd2e5f;
       public         postgres    false    187            "           1259    121314     anagrafica_appartenenza_7df656af    INDEX     _   CREATE INDEX anagrafica_appartenenza_7df656af ON anagrafica_appartenenza USING btree (inizio);
 4   DROP INDEX public.anagrafica_appartenenza_7df656af;
       public         postgres    false    187            #           1259    121315     anagrafica_appartenenza_9364fb87    INDEX     _   CREATE INDEX anagrafica_appartenenza_9364fb87 ON anagrafica_appartenenza USING btree (membro);
 4   DROP INDEX public.anagrafica_appartenenza_9364fb87;
       public         postgres    false    187            $           1259    121316 /   anagrafica_appartenenza_confermata_6dc30a80_idx    INDEX     ~   CREATE INDEX anagrafica_appartenenza_confermata_6dc30a80_idx ON anagrafica_appartenenza USING btree (confermata, persona_id);
 C   DROP INDEX public.anagrafica_appartenenza_confermata_6dc30a80_idx;
       public         postgres    false    187    187            %           1259    121317     anagrafica_appartenenza_e8589820    INDEX     c   CREATE INDEX anagrafica_appartenenza_e8589820 ON anagrafica_appartenenza USING btree (persona_id);
 4   DROP INDEX public.anagrafica_appartenenza_e8589820;
       public         postgres    false    187            &           1259    121318     anagrafica_appartenenza_ed4272b5    INDEX     e   CREATE INDEX anagrafica_appartenenza_ed4272b5 ON anagrafica_appartenenza USING btree (terminazione);
 4   DROP INDEX public.anagrafica_appartenenza_ed4272b5;
       public         postgres    false    187            '           1259    121319     anagrafica_appartenenza_fff25994    INDEX     ]   CREATE INDEX anagrafica_appartenenza_fff25994 ON anagrafica_appartenenza USING btree (fine);
 4   DROP INDEX public.anagrafica_appartenenza_fff25994;
       public         postgres    false    187            (           1259    121320 '   anagrafica_appartenenza_id_c708bd84_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_id_c708bd84_idx ON anagrafica_appartenenza USING btree (id, sede_id, membro, inizio, fine);
 ;   DROP INDEX public.anagrafica_appartenenza_id_c708bd84_idx;
       public         postgres    false    187    187    187    187    187            )           1259    121322 +   anagrafica_appartenenza_inizio_b1953360_idx    INDEX     p   CREATE INDEX anagrafica_appartenenza_inizio_b1953360_idx ON anagrafica_appartenenza USING btree (inizio, fine);
 ?   DROP INDEX public.anagrafica_appartenenza_inizio_b1953360_idx;
       public         postgres    false    187    187            *           1259    121323 +   anagrafica_appartenenza_membro_8432f1cd_idx    INDEX     v   CREATE INDEX anagrafica_appartenenza_membro_8432f1cd_idx ON anagrafica_appartenenza USING btree (membro, confermata);
 ?   DROP INDEX public.anagrafica_appartenenza_membro_8432f1cd_idx;
       public         postgres    false    187    187            +           1259    121324 +   anagrafica_appartenenza_membro_996b60da_idx    INDEX        CREATE INDEX anagrafica_appartenenza_membro_996b60da_idx ON anagrafica_appartenenza USING btree (membro, confermata, sede_id);
 ?   DROP INDEX public.anagrafica_appartenenza_membro_996b60da_idx;
       public         postgres    false    187    187    187            ,           1259    121325 ,   anagrafica_appartenenza_membro_9bb43ea0_like    INDEX        CREATE INDEX anagrafica_appartenenza_membro_9bb43ea0_like ON anagrafica_appartenenza USING btree (membro varchar_pattern_ops);
 @   DROP INDEX public.anagrafica_appartenenza_membro_9bb43ea0_like;
       public         postgres    false    187            -           1259    121331 +   anagrafica_appartenenza_membro_a33e6688_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_membro_a33e6688_idx ON anagrafica_appartenenza USING btree (membro, confermata, persona_id);
 ?   DROP INDEX public.anagrafica_appartenenza_membro_a33e6688_idx;
       public         postgres    false    187    187    187            .           1259    121332 +   anagrafica_appartenenza_membro_ab39a013_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_membro_ab39a013_idx ON anagrafica_appartenenza USING btree (membro, confermata, inizio, fine);
 ?   DROP INDEX public.anagrafica_appartenenza_membro_ab39a013_idx;
       public         postgres    false    187    187    187    187            /           1259    121333 /   anagrafica_appartenenza_persona_id_03960659_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_persona_id_03960659_idx ON anagrafica_appartenenza USING btree (persona_id, inizio, fine, membro);
 C   DROP INDEX public.anagrafica_appartenenza_persona_id_03960659_idx;
       public         postgres    false    187    187    187    187            0           1259    121334 /   anagrafica_appartenenza_persona_id_2091c263_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_persona_id_2091c263_idx ON anagrafica_appartenenza USING btree (persona_id, inizio, fine);
 C   DROP INDEX public.anagrafica_appartenenza_persona_id_2091c263_idx;
       public         postgres    false    187    187    187            1           1259    121335 /   anagrafica_appartenenza_persona_id_65a301f6_idx    INDEX     {   CREATE INDEX anagrafica_appartenenza_persona_id_65a301f6_idx ON anagrafica_appartenenza USING btree (persona_id, sede_id);
 C   DROP INDEX public.anagrafica_appartenenza_persona_id_65a301f6_idx;
       public         postgres    false    187    187            2           1259    121336 /   anagrafica_appartenenza_persona_id_7cf4ad5e_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_persona_id_7cf4ad5e_idx ON anagrafica_appartenenza USING btree (persona_id, inizio, fine, membro, confermata);
 C   DROP INDEX public.anagrafica_appartenenza_persona_id_7cf4ad5e_idx;
       public         postgres    false    187    187    187    187    187            5           1259    121338 ,   anagrafica_appartenenza_sede_id_2ae5876d_idx    INDEX     z   CREATE INDEX anagrafica_appartenenza_sede_id_2ae5876d_idx ON anagrafica_appartenenza USING btree (sede_id, inizio, fine);
 @   DROP INDEX public.anagrafica_appartenenza_sede_id_2ae5876d_idx;
       public         postgres    false    187    187    187            6           1259    121339 ,   anagrafica_appartenenza_sede_id_c7c375fa_idx    INDEX     �   CREATE INDEX anagrafica_appartenenza_sede_id_c7c375fa_idx ON anagrafica_appartenenza USING btree (sede_id, membro, inizio, fine);
 @   DROP INDEX public.anagrafica_appartenenza_sede_id_c7c375fa_idx;
       public         postgres    false    187    187    187    187            7           1259    121340 ,   anagrafica_appartenenza_sede_id_ecc36d22_idx    INDEX     t   CREATE INDEX anagrafica_appartenenza_sede_id_ecc36d22_idx ON anagrafica_appartenenza USING btree (sede_id, membro);
 @   DROP INDEX public.anagrafica_appartenenza_sede_id_ecc36d22_idx;
       public         postgres    false    187    187            8           1259    121341 2   anagrafica_appartenenza_terminazione_428ebe50_like    INDEX     �   CREATE INDEX anagrafica_appartenenza_terminazione_428ebe50_like ON anagrafica_appartenenza USING btree (terminazione varchar_pattern_ops);
 F   DROP INDEX public.anagrafica_appartenenza_terminazione_428ebe50_like;
       public         postgres    false    187            9           1259    121342    anagrafica_delega_36063dc9    INDEX     V   CREATE INDEX anagrafica_delega_36063dc9 ON anagrafica_delega USING btree (creazione);
 .   DROP INDEX public.anagrafica_delega_36063dc9;
       public         postgres    false    189            :           1259    121343    anagrafica_delega_401281b0    INDEX     Q   CREATE INDEX anagrafica_delega_401281b0 ON anagrafica_delega USING btree (tipo);
 .   DROP INDEX public.anagrafica_delega_401281b0;
       public         postgres    false    189            ;           1259    121344    anagrafica_delega_515fa17e    INDEX     Z   CREATE INDEX anagrafica_delega_515fa17e ON anagrafica_delega USING btree (firmatario_id);
 .   DROP INDEX public.anagrafica_delega_515fa17e;
       public         postgres    false    189            <           1259    121345    anagrafica_delega_69bd2e5f    INDEX     \   CREATE INDEX anagrafica_delega_69bd2e5f ON anagrafica_delega USING btree (ultima_modifica);
 .   DROP INDEX public.anagrafica_delega_69bd2e5f;
       public         postgres    false    189            =           1259    121349    anagrafica_delega_7df656af    INDEX     S   CREATE INDEX anagrafica_delega_7df656af ON anagrafica_delega USING btree (inizio);
 .   DROP INDEX public.anagrafica_delega_7df656af;
       public         postgres    false    189            >           1259    121350    anagrafica_delega_9c82ce86    INDEX     W   CREATE INDEX anagrafica_delega_9c82ce86 ON anagrafica_delega USING btree (oggetto_id);
 .   DROP INDEX public.anagrafica_delega_9c82ce86;
       public         postgres    false    189            ?           1259    121351    anagrafica_delega_e8589820    INDEX     W   CREATE INDEX anagrafica_delega_e8589820 ON anagrafica_delega USING btree (persona_id);
 .   DROP INDEX public.anagrafica_delega_e8589820;
       public         postgres    false    189            @           1259    121352    anagrafica_delega_fe2a0979    INDEX     \   CREATE INDEX anagrafica_delega_fe2a0979 ON anagrafica_delega USING btree (oggetto_tipo_id);
 .   DROP INDEX public.anagrafica_delega_fe2a0979;
       public         postgres    false    189            A           1259    121353    anagrafica_delega_fff25994    INDEX     Q   CREATE INDEX anagrafica_delega_fff25994 ON anagrafica_delega USING btree (fine);
 .   DROP INDEX public.anagrafica_delega_fff25994;
       public         postgres    false    189            B           1259    121354 %   anagrafica_delega_inizio_12d1cd58_idx    INDEX     d   CREATE INDEX anagrafica_delega_inizio_12d1cd58_idx ON anagrafica_delega USING btree (inizio, fine);
 9   DROP INDEX public.anagrafica_delega_inizio_12d1cd58_idx;
       public         postgres    false    189    189            C           1259    121355 %   anagrafica_delega_inizio_85ba6481_idx    INDEX     �   CREATE INDEX anagrafica_delega_inizio_85ba6481_idx ON anagrafica_delega USING btree (inizio, fine, tipo, oggetto_id, oggetto_tipo_id);
 9   DROP INDEX public.anagrafica_delega_inizio_85ba6481_idx;
       public         postgres    false    189    189    189    189    189            D           1259    121356 %   anagrafica_delega_inizio_9f1c70a8_idx    INDEX     j   CREATE INDEX anagrafica_delega_inizio_9f1c70a8_idx ON anagrafica_delega USING btree (inizio, fine, tipo);
 9   DROP INDEX public.anagrafica_delega_inizio_9f1c70a8_idx;
       public         postgres    false    189    189    189            E           1259    121357 .   anagrafica_delega_oggetto_tipo_id_6bdb9373_idx    INDEX     |   CREATE INDEX anagrafica_delega_oggetto_tipo_id_6bdb9373_idx ON anagrafica_delega USING btree (oggetto_tipo_id, oggetto_id);
 B   DROP INDEX public.anagrafica_delega_oggetto_tipo_id_6bdb9373_idx;
       public         postgres    false    189    189            F           1259    121358 )   anagrafica_delega_persona_id_2cbc7c88_idx    INDEX     t   CREATE INDEX anagrafica_delega_persona_id_2cbc7c88_idx ON anagrafica_delega USING btree (persona_id, inizio, fine);
 =   DROP INDEX public.anagrafica_delega_persona_id_2cbc7c88_idx;
       public         postgres    false    189    189    189            G           1259    121359 )   anagrafica_delega_persona_id_504b3bbb_idx    INDEX     z   CREATE INDEX anagrafica_delega_persona_id_504b3bbb_idx ON anagrafica_delega USING btree (persona_id, inizio, fine, tipo);
 =   DROP INDEX public.anagrafica_delega_persona_id_504b3bbb_idx;
       public         postgres    false    189    189    189    189            H           1259    121360 )   anagrafica_delega_persona_id_98188654_idx    INDEX     l   CREATE INDEX anagrafica_delega_persona_id_98188654_idx ON anagrafica_delega USING btree (persona_id, tipo);
 =   DROP INDEX public.anagrafica_delega_persona_id_98188654_idx;
       public         postgres    false    189    189            I           1259    121361 )   anagrafica_delega_persona_id_ca68c76e_idx    INDEX     �   CREATE INDEX anagrafica_delega_persona_id_ca68c76e_idx ON anagrafica_delega USING btree (persona_id, inizio, fine, tipo, oggetto_id, oggetto_tipo_id);
 =   DROP INDEX public.anagrafica_delega_persona_id_ca68c76e_idx;
       public         postgres    false    189    189    189    189    189    189            L           1259    121362 #   anagrafica_delega_tipo_d237ebb0_idx    INDEX     w   CREATE INDEX anagrafica_delega_tipo_d237ebb0_idx ON anagrafica_delega USING btree (tipo, oggetto_tipo_id, oggetto_id);
 7   DROP INDEX public.anagrafica_delega_tipo_d237ebb0_idx;
       public         postgres    false    189    189    189            M           1259    121363 $   anagrafica_delega_tipo_f5abc5c5_like    INDEX     o   CREATE INDEX anagrafica_delega_tipo_f5abc5c5_like ON anagrafica_delega USING btree (tipo varchar_pattern_ops);
 8   DROP INDEX public.anagrafica_delega_tipo_f5abc5c5_like;
       public         postgres    false    189            N           1259    121364    anagrafica_dimissione_0687f864    INDEX     \   CREATE INDEX anagrafica_dimissione_0687f864 ON anagrafica_dimissione USING btree (sede_id);
 2   DROP INDEX public.anagrafica_dimissione_0687f864;
       public         postgres    false    191            O           1259    121365    anagrafica_dimissione_36063dc9    INDEX     ^   CREATE INDEX anagrafica_dimissione_36063dc9 ON anagrafica_dimissione USING btree (creazione);
 2   DROP INDEX public.anagrafica_dimissione_36063dc9;
       public         postgres    false    191            P           1259    121366    anagrafica_dimissione_530b0ac8    INDEX     d   CREATE INDEX anagrafica_dimissione_530b0ac8 ON anagrafica_dimissione USING btree (appartenenza_id);
 2   DROP INDEX public.anagrafica_dimissione_530b0ac8;
       public         postgres    false    191            Q           1259    121367    anagrafica_dimissione_69bd2e5f    INDEX     d   CREATE INDEX anagrafica_dimissione_69bd2e5f ON anagrafica_dimissione USING btree (ultima_modifica);
 2   DROP INDEX public.anagrafica_dimissione_69bd2e5f;
       public         postgres    false    191            R           1259    121368    anagrafica_dimissione_e3692faf    INDEX     c   CREATE INDEX anagrafica_dimissione_e3692faf ON anagrafica_dimissione USING btree (richiedente_id);
 2   DROP INDEX public.anagrafica_dimissione_e3692faf;
       public         postgres    false    191            S           1259    121369    anagrafica_dimissione_e8589820    INDEX     _   CREATE INDEX anagrafica_dimissione_e8589820 ON anagrafica_dimissione USING btree (persona_id);
 2   DROP INDEX public.anagrafica_dimissione_e8589820;
       public         postgres    false    191            V           1259    121370    anagrafica_documento_36063dc9    INDEX     \   CREATE INDEX anagrafica_documento_36063dc9 ON anagrafica_documento USING btree (creazione);
 1   DROP INDEX public.anagrafica_documento_36063dc9;
       public         postgres    false    193            W           1259    121371    anagrafica_documento_401281b0    INDEX     W   CREATE INDEX anagrafica_documento_401281b0 ON anagrafica_documento USING btree (tipo);
 1   DROP INDEX public.anagrafica_documento_401281b0;
       public         postgres    false    193            X           1259    121372    anagrafica_documento_69bd2e5f    INDEX     b   CREATE INDEX anagrafica_documento_69bd2e5f ON anagrafica_documento USING btree (ultima_modifica);
 1   DROP INDEX public.anagrafica_documento_69bd2e5f;
       public         postgres    false    193            Y           1259    121373    anagrafica_documento_e8589820    INDEX     ]   CREATE INDEX anagrafica_documento_e8589820 ON anagrafica_documento USING btree (persona_id);
 1   DROP INDEX public.anagrafica_documento_e8589820;
       public         postgres    false    193            \           1259    121374 '   anagrafica_documento_tipo_643d2179_like    INDEX     u   CREATE INDEX anagrafica_documento_tipo_643d2179_like ON anagrafica_documento USING btree (tipo varchar_pattern_ops);
 ;   DROP INDEX public.anagrafica_documento_tipo_643d2179_like;
       public         postgres    false    193            ]           1259    121375    anagrafica_estensione_36063dc9    INDEX     ^   CREATE INDEX anagrafica_estensione_36063dc9 ON anagrafica_estensione USING btree (creazione);
 2   DROP INDEX public.anagrafica_estensione_36063dc9;
       public         postgres    false    195            ^           1259    121376    anagrafica_estensione_43662d06    INDEX     _   CREATE INDEX anagrafica_estensione_43662d06 ON anagrafica_estensione USING btree (confermata);
 2   DROP INDEX public.anagrafica_estensione_43662d06;
       public         postgres    false    195            _           1259    121377    anagrafica_estensione_4a9487af    INDEX     ]   CREATE INDEX anagrafica_estensione_4a9487af ON anagrafica_estensione USING btree (ritirata);
 2   DROP INDEX public.anagrafica_estensione_4a9487af;
       public         postgres    false    195            `           1259    121378    anagrafica_estensione_530b0ac8    INDEX     d   CREATE INDEX anagrafica_estensione_530b0ac8 ON anagrafica_estensione USING btree (appartenenza_id);
 2   DROP INDEX public.anagrafica_estensione_530b0ac8;
       public         postgres    false    195            a           1259    121379    anagrafica_estensione_69bd2e5f    INDEX     d   CREATE INDEX anagrafica_estensione_69bd2e5f ON anagrafica_estensione USING btree (ultima_modifica);
 2   DROP INDEX public.anagrafica_estensione_69bd2e5f;
       public         postgres    false    195            b           1259    121380    anagrafica_estensione_cb8e6a80    INDEX     d   CREATE INDEX anagrafica_estensione_cb8e6a80 ON anagrafica_estensione USING btree (destinazione_id);
 2   DROP INDEX public.anagrafica_estensione_cb8e6a80;
       public         postgres    false    195            c           1259    121381    anagrafica_estensione_e3692faf    INDEX     c   CREATE INDEX anagrafica_estensione_e3692faf ON anagrafica_estensione USING btree (richiedente_id);
 2   DROP INDEX public.anagrafica_estensione_e3692faf;
       public         postgres    false    195            d           1259    121382    anagrafica_estensione_e8589820    INDEX     _   CREATE INDEX anagrafica_estensione_e8589820 ON anagrafica_estensione USING btree (persona_id);
 2   DROP INDEX public.anagrafica_estensione_e8589820;
       public         postgres    false    195            g           1259    121383    anagrafica_fototessera_36063dc9    INDEX     `   CREATE INDEX anagrafica_fototessera_36063dc9 ON anagrafica_fototessera USING btree (creazione);
 3   DROP INDEX public.anagrafica_fototessera_36063dc9;
       public         postgres    false    197            h           1259    121384    anagrafica_fototessera_43662d06    INDEX     a   CREATE INDEX anagrafica_fototessera_43662d06 ON anagrafica_fototessera USING btree (confermata);
 3   DROP INDEX public.anagrafica_fototessera_43662d06;
       public         postgres    false    197            i           1259    121385    anagrafica_fototessera_4a9487af    INDEX     _   CREATE INDEX anagrafica_fototessera_4a9487af ON anagrafica_fototessera USING btree (ritirata);
 3   DROP INDEX public.anagrafica_fototessera_4a9487af;
       public         postgres    false    197            j           1259    121386    anagrafica_fototessera_69bd2e5f    INDEX     f   CREATE INDEX anagrafica_fototessera_69bd2e5f ON anagrafica_fototessera USING btree (ultima_modifica);
 3   DROP INDEX public.anagrafica_fototessera_69bd2e5f;
       public         postgres    false    197            k           1259    121387    anagrafica_fototessera_e8589820    INDEX     a   CREATE INDEX anagrafica_fototessera_e8589820 ON anagrafica_fototessera USING btree (persona_id);
 3   DROP INDEX public.anagrafica_fototessera_e8589820;
       public         postgres    false    197            n           1259    121388    anagrafica_persona_04f07280    INDEX     ^   CREATE INDEX anagrafica_persona_04f07280 ON anagrafica_persona USING btree (privacy_deleghe);
 /   DROP INDEX public.anagrafica_persona_04f07280;
       public         postgres    false    199            o           1259    121389    anagrafica_persona_313902d5    INDEX     U   CREATE INDEX anagrafica_persona_313902d5 ON anagrafica_persona USING btree (genere);
 /   DROP INDEX public.anagrafica_persona_313902d5;
       public         postgres    false    199            p           1259    121390    anagrafica_persona_36063dc9    INDEX     X   CREATE INDEX anagrafica_persona_36063dc9 ON anagrafica_persona USING btree (creazione);
 /   DROP INDEX public.anagrafica_persona_36063dc9;
       public         postgres    false    199            q           1259    121391    anagrafica_persona_69bd2e5f    INDEX     ^   CREATE INDEX anagrafica_persona_69bd2e5f ON anagrafica_persona USING btree (ultima_modifica);
 /   DROP INDEX public.anagrafica_persona_69bd2e5f;
       public         postgres    false    199            r           1259    121392    anagrafica_persona_798a16e8    INDEX     [   CREATE INDEX anagrafica_persona_798a16e8 ON anagrafica_persona USING btree (data_nascita);
 /   DROP INDEX public.anagrafica_persona_798a16e8;
       public         postgres    false    199            s           1259    121393    anagrafica_persona_820eb5b6    INDEX     Q   CREATE INDEX anagrafica_persona_820eb5b6 ON anagrafica_persona USING btree (cm);
 /   DROP INDEX public.anagrafica_persona_820eb5b6;
       public         postgres    false    199            t           1259    121394    anagrafica_persona_aed6a6bc    INDEX     a   CREATE INDEX anagrafica_persona_aed6a6bc ON anagrafica_persona USING btree (privacy_curriculum);
 /   DROP INDEX public.anagrafica_persona_aed6a6bc;
       public         postgres    false    199            u           1259    121395    anagrafica_persona_c6d86a4e    INDEX     Y   CREATE INDEX anagrafica_persona_c6d86a4e ON anagrafica_persona USING btree (conoscenza);
 /   DROP INDEX public.anagrafica_persona_c6d86a4e;
       public         postgres    false    199            v           1259    121396 /   anagrafica_persona_codice_fiscale_1583088a_like    INDEX     �   CREATE INDEX anagrafica_persona_codice_fiscale_1583088a_like ON anagrafica_persona USING btree (codice_fiscale varchar_pattern_ops);
 C   DROP INDEX public.anagrafica_persona_codice_fiscale_1583088a_like;
       public         postgres    false    199            y           1259    121397 (   anagrafica_persona_cognome_bd30736c_like    INDEX     w   CREATE INDEX anagrafica_persona_cognome_bd30736c_like ON anagrafica_persona USING btree (cognome varchar_pattern_ops);
 <   DROP INDEX public.anagrafica_persona_cognome_bd30736c_like;
       public         postgres    false    199            z           1259    121398 (   anagrafica_persona_cognome_bd30736c_uniq    INDEX     c   CREATE INDEX anagrafica_persona_cognome_bd30736c_uniq ON anagrafica_persona USING btree (cognome);
 <   DROP INDEX public.anagrafica_persona_cognome_bd30736c_uniq;
       public         postgres    false    199            {           1259    121399    anagrafica_persona_d6ef5c1f    INDEX     Y   CREATE INDEX anagrafica_persona_d6ef5c1f ON anagrafica_persona USING btree (vecchio_id);
 /   DROP INDEX public.anagrafica_persona_d6ef5c1f;
       public         postgres    false    199            |           1259    121400    anagrafica_persona_e0b406f5    INDEX     T   CREATE INDEX anagrafica_persona_e0b406f5 ON anagrafica_persona USING btree (stato);
 /   DROP INDEX public.anagrafica_persona_e0b406f5;
       public         postgres    false    199            }           1259    121401    anagrafica_persona_f0b53b2d    INDEX     Q   CREATE INDEX anagrafica_persona_f0b53b2d ON anagrafica_persona USING btree (iv);
 /   DROP INDEX public.anagrafica_persona_f0b53b2d;
       public         postgres    false    199            ~           1259    121402    anagrafica_persona_f2ff7cbe    INDEX     _   CREATE INDEX anagrafica_persona_f2ff7cbe ON anagrafica_persona USING btree (privacy_contatti);
 /   DROP INDEX public.anagrafica_persona_f2ff7cbe;
       public         postgres    false    199                       1259    121403 '   anagrafica_persona_genere_eca23be3_like    INDEX     u   CREATE INDEX anagrafica_persona_genere_eca23be3_like ON anagrafica_persona USING btree (genere varchar_pattern_ops);
 ;   DROP INDEX public.anagrafica_persona_genere_eca23be3_like;
       public         postgres    false    199            �           1259    121404 "   anagrafica_persona_id_8ad8c544_idx    INDEX     w   CREATE INDEX anagrafica_persona_id_8ad8c544_idx ON anagrafica_persona USING btree (id, nome, cognome, codice_fiscale);
 6   DROP INDEX public.anagrafica_persona_id_8ad8c544_idx;
       public         postgres    false    199    199    199    199            �           1259    121405 %   anagrafica_persona_nome_70081da9_like    INDEX     q   CREATE INDEX anagrafica_persona_nome_70081da9_like ON anagrafica_persona USING btree (nome varchar_pattern_ops);
 9   DROP INDEX public.anagrafica_persona_nome_70081da9_like;
       public         postgres    false    199            �           1259    121406 %   anagrafica_persona_nome_70081da9_uniq    INDEX     ]   CREATE INDEX anagrafica_persona_nome_70081da9_uniq ON anagrafica_persona USING btree (nome);
 9   DROP INDEX public.anagrafica_persona_nome_70081da9_uniq;
       public         postgres    false    199            �           1259    121407 $   anagrafica_persona_nome_d0a64a88_idx    INDEX     e   CREATE INDEX anagrafica_persona_nome_d0a64a88_idx ON anagrafica_persona USING btree (nome, cognome);
 8   DROP INDEX public.anagrafica_persona_nome_d0a64a88_idx;
       public         postgres    false    199    199            �           1259    121408 $   anagrafica_persona_nome_d6ba09ab_idx    INDEX     u   CREATE INDEX anagrafica_persona_nome_d6ba09ab_idx ON anagrafica_persona USING btree (nome, cognome, codice_fiscale);
 8   DROP INDEX public.anagrafica_persona_nome_d6ba09ab_idx;
       public         postgres    false    199    199    199            �           1259    121409 &   anagrafica_persona_stato_b8b12958_like    INDEX     s   CREATE INDEX anagrafica_persona_stato_b8b12958_like ON anagrafica_persona USING btree (stato varchar_pattern_ops);
 :   DROP INDEX public.anagrafica_persona_stato_b8b12958_like;
       public         postgres    false    199            �           1259    121410 -   anagrafica_provvedimentodisciplinare_0687f864    INDEX     z   CREATE INDEX anagrafica_provvedimentodisciplinare_0687f864 ON anagrafica_provvedimentodisciplinare USING btree (sede_id);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_0687f864;
       public         postgres    false    201            �           1259    121411 -   anagrafica_provvedimentodisciplinare_36063dc9    INDEX     |   CREATE INDEX anagrafica_provvedimentodisciplinare_36063dc9 ON anagrafica_provvedimentodisciplinare USING btree (creazione);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_36063dc9;
       public         postgres    false    201            �           1259    121412 -   anagrafica_provvedimentodisciplinare_5744ea4d    INDEX     �   CREATE INDEX anagrafica_provvedimentodisciplinare_5744ea4d ON anagrafica_provvedimentodisciplinare USING btree (registrato_da_id);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_5744ea4d;
       public         postgres    false    201            �           1259    121413 -   anagrafica_provvedimentodisciplinare_69bd2e5f    INDEX     �   CREATE INDEX anagrafica_provvedimentodisciplinare_69bd2e5f ON anagrafica_provvedimentodisciplinare USING btree (ultima_modifica);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_69bd2e5f;
       public         postgres    false    201            �           1259    121414 -   anagrafica_provvedimentodisciplinare_7df656af    INDEX     y   CREATE INDEX anagrafica_provvedimentodisciplinare_7df656af ON anagrafica_provvedimentodisciplinare USING btree (inizio);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_7df656af;
       public         postgres    false    201            �           1259    121415 -   anagrafica_provvedimentodisciplinare_e8589820    INDEX     }   CREATE INDEX anagrafica_provvedimentodisciplinare_e8589820 ON anagrafica_provvedimentodisciplinare USING btree (persona_id);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_e8589820;
       public         postgres    false    201            �           1259    121416 -   anagrafica_provvedimentodisciplinare_fff25994    INDEX     w   CREATE INDEX anagrafica_provvedimentodisciplinare_fff25994 ON anagrafica_provvedimentodisciplinare USING btree (fine);
 A   DROP INDEX public.anagrafica_provvedimentodisciplinare_fff25994;
       public         postgres    false    201            �           1259    121417    anagrafica_riserva_36063dc9    INDEX     X   CREATE INDEX anagrafica_riserva_36063dc9 ON anagrafica_riserva USING btree (creazione);
 /   DROP INDEX public.anagrafica_riserva_36063dc9;
       public         postgres    false    203            �           1259    121418    anagrafica_riserva_43662d06    INDEX     Y   CREATE INDEX anagrafica_riserva_43662d06 ON anagrafica_riserva USING btree (confermata);
 /   DROP INDEX public.anagrafica_riserva_43662d06;
       public         postgres    false    203            �           1259    121419    anagrafica_riserva_4a9487af    INDEX     W   CREATE INDEX anagrafica_riserva_4a9487af ON anagrafica_riserva USING btree (ritirata);
 /   DROP INDEX public.anagrafica_riserva_4a9487af;
       public         postgres    false    203            �           1259    121420    anagrafica_riserva_530b0ac8    INDEX     ^   CREATE INDEX anagrafica_riserva_530b0ac8 ON anagrafica_riserva USING btree (appartenenza_id);
 /   DROP INDEX public.anagrafica_riserva_530b0ac8;
       public         postgres    false    203            �           1259    121421    anagrafica_riserva_69bd2e5f    INDEX     ^   CREATE INDEX anagrafica_riserva_69bd2e5f ON anagrafica_riserva USING btree (ultima_modifica);
 /   DROP INDEX public.anagrafica_riserva_69bd2e5f;
       public         postgres    false    203            �           1259    121422    anagrafica_riserva_7df656af    INDEX     U   CREATE INDEX anagrafica_riserva_7df656af ON anagrafica_riserva USING btree (inizio);
 /   DROP INDEX public.anagrafica_riserva_7df656af;
       public         postgres    false    203            �           1259    121423    anagrafica_riserva_e8589820    INDEX     Y   CREATE INDEX anagrafica_riserva_e8589820 ON anagrafica_riserva USING btree (persona_id);
 /   DROP INDEX public.anagrafica_riserva_e8589820;
       public         postgres    false    203            �           1259    121424    anagrafica_riserva_fff25994    INDEX     S   CREATE INDEX anagrafica_riserva_fff25994 ON anagrafica_riserva USING btree (fine);
 /   DROP INDEX public.anagrafica_riserva_fff25994;
       public         postgres    false    203            �           1259    121425 &   anagrafica_riserva_inizio_f8af8216_idx    INDEX     f   CREATE INDEX anagrafica_riserva_inizio_f8af8216_idx ON anagrafica_riserva USING btree (inizio, fine);
 :   DROP INDEX public.anagrafica_riserva_inizio_f8af8216_idx;
       public         postgres    false    203    203            �           1259    121426 *   anagrafica_riserva_persona_id_5ee09e53_idx    INDEX     v   CREATE INDEX anagrafica_riserva_persona_id_5ee09e53_idx ON anagrafica_riserva USING btree (persona_id, inizio, fine);
 >   DROP INDEX public.anagrafica_riserva_persona_id_5ee09e53_idx;
       public         postgres    false    203    203    203            �           1259    121427    anagrafica_sede_28576d3a    INDEX     O   CREATE INDEX anagrafica_sede_28576d3a ON anagrafica_sede USING btree (attiva);
 ,   DROP INDEX public.anagrafica_sede_28576d3a;
       public         postgres    false    205            �           1259    121428    anagrafica_sede_29a104e3    INDEX     U   CREATE INDEX anagrafica_sede_29a104e3 ON anagrafica_sede USING btree (locazione_id);
 ,   DROP INDEX public.anagrafica_sede_29a104e3;
       public         postgres    false    205            �           1259    121429    anagrafica_sede_2dbcba41    INDEX     M   CREATE INDEX anagrafica_sede_2dbcba41 ON anagrafica_sede USING btree (slug);
 ,   DROP INDEX public.anagrafica_sede_2dbcba41;
       public         postgres    false    205            �           1259    121430    anagrafica_sede_36063dc9    INDEX     R   CREATE INDEX anagrafica_sede_36063dc9 ON anagrafica_sede USING btree (creazione);
 ,   DROP INDEX public.anagrafica_sede_36063dc9;
       public         postgres    false    205            �           1259    121431    anagrafica_sede_3cfbd988    INDEX     M   CREATE INDEX anagrafica_sede_3cfbd988 ON anagrafica_sede USING btree (rght);
 ,   DROP INDEX public.anagrafica_sede_3cfbd988;
       public         postgres    false    205            �           1259    121432    anagrafica_sede_401281b0    INDEX     M   CREATE INDEX anagrafica_sede_401281b0 ON anagrafica_sede USING btree (tipo);
 ,   DROP INDEX public.anagrafica_sede_401281b0;
       public         postgres    false    205            �           1259    121433    anagrafica_sede_656442a0    INDEX     P   CREATE INDEX anagrafica_sede_656442a0 ON anagrafica_sede USING btree (tree_id);
 ,   DROP INDEX public.anagrafica_sede_656442a0;
       public         postgres    false    205            �           1259    121434    anagrafica_sede_666ac576    INDEX     M   CREATE INDEX anagrafica_sede_666ac576 ON anagrafica_sede USING btree (nome);
 ,   DROP INDEX public.anagrafica_sede_666ac576;
       public         postgres    false    205            �           1259    121435    anagrafica_sede_69bd2e5f    INDEX     X   CREATE INDEX anagrafica_sede_69bd2e5f ON anagrafica_sede USING btree (ultima_modifica);
 ,   DROP INDEX public.anagrafica_sede_69bd2e5f;
       public         postgres    false    205            �           1259    121436 #   anagrafica_sede_attiva_233f988f_idx    INDEX     f   CREATE INDEX anagrafica_sede_attiva_233f988f_idx ON anagrafica_sede USING btree (attiva, estensione);
 7   DROP INDEX public.anagrafica_sede_attiva_233f988f_idx;
       public         postgres    false    205    205            �           1259    121437 #   anagrafica_sede_attiva_7fd691e4_idx    INDEX     `   CREATE INDEX anagrafica_sede_attiva_7fd691e4_idx ON anagrafica_sede USING btree (attiva, tipo);
 7   DROP INDEX public.anagrafica_sede_attiva_7fd691e4_idx;
       public         postgres    false    205    205            �           1259    121438    anagrafica_sede_c9e9a848    INDEX     N   CREATE INDEX anagrafica_sede_c9e9a848 ON anagrafica_sede USING btree (level);
 ,   DROP INDEX public.anagrafica_sede_c9e9a848;
       public         postgres    false    205            �           1259    121439    anagrafica_sede_caf7cc51    INDEX     L   CREATE INDEX anagrafica_sede_caf7cc51 ON anagrafica_sede USING btree (lft);
 ,   DROP INDEX public.anagrafica_sede_caf7cc51;
       public         postgres    false    205            �           1259    121440    anagrafica_sede_d6ef5c1f    INDEX     S   CREATE INDEX anagrafica_sede_d6ef5c1f ON anagrafica_sede USING btree (vecchio_id);
 ,   DROP INDEX public.anagrafica_sede_d6ef5c1f;
       public         postgres    false    205            �           1259    121441    anagrafica_sede_dbb9a234    INDEX     S   CREATE INDEX anagrafica_sede_dbb9a234 ON anagrafica_sede USING btree (estensione);
 ,   DROP INDEX public.anagrafica_sede_dbb9a234;
       public         postgres    false    205            �           1259    121442    anagrafica_sede_e3246201    INDEX     T   CREATE INDEX anagrafica_sede_e3246201 ON anagrafica_sede USING btree (genitore_id);
 ,   DROP INDEX public.anagrafica_sede_e3246201;
       public         postgres    false    205            �           1259    121443 (   anagrafica_sede_estensione_b209debc_like    INDEX     w   CREATE INDEX anagrafica_sede_estensione_b209debc_like ON anagrafica_sede USING btree (estensione varchar_pattern_ops);
 <   DROP INDEX public.anagrafica_sede_estensione_b209debc_like;
       public         postgres    false    205            �           1259    121444 '   anagrafica_sede_estensione_cccb80d7_idx    INDEX     h   CREATE INDEX anagrafica_sede_estensione_cccb80d7_idx ON anagrafica_sede USING btree (estensione, tipo);
 ;   DROP INDEX public.anagrafica_sede_estensione_cccb80d7_idx;
       public         postgres    false    205    205            �           1259    121445 (   anagrafica_sede_genitore_id_b098ef17_idx    INDEX     p   CREATE INDEX anagrafica_sede_genitore_id_b098ef17_idx ON anagrafica_sede USING btree (genitore_id, estensione);
 <   DROP INDEX public.anagrafica_sede_genitore_id_b098ef17_idx;
       public         postgres    false    205    205            �           1259    121446     anagrafica_sede_lft_05961abf_idx    INDEX     b   CREATE INDEX anagrafica_sede_lft_05961abf_idx ON anagrafica_sede USING btree (lft, rght, attiva);
 4   DROP INDEX public.anagrafica_sede_lft_05961abf_idx;
       public         postgres    false    205    205    205            �           1259    121447     anagrafica_sede_lft_b9e067ed_idx    INDEX     c   CREATE INDEX anagrafica_sede_lft_b9e067ed_idx ON anagrafica_sede USING btree (lft, rght, tree_id);
 4   DROP INDEX public.anagrafica_sede_lft_b9e067ed_idx;
       public         postgres    false    205    205    205            �           1259    121448     anagrafica_sede_lft_e582fb51_idx    INDEX     Z   CREATE INDEX anagrafica_sede_lft_e582fb51_idx ON anagrafica_sede USING btree (lft, rght);
 4   DROP INDEX public.anagrafica_sede_lft_e582fb51_idx;
       public         postgres    false    205    205            �           1259    121449     anagrafica_sede_lft_ee02f9f7_idx    INDEX     n   CREATE INDEX anagrafica_sede_lft_ee02f9f7_idx ON anagrafica_sede USING btree (lft, rght, attiva, estensione);
 4   DROP INDEX public.anagrafica_sede_lft_ee02f9f7_idx;
       public         postgres    false    205    205    205    205            �           1259    121450 "   anagrafica_sede_nome_b7509597_like    INDEX     k   CREATE INDEX anagrafica_sede_nome_b7509597_like ON anagrafica_sede USING btree (nome varchar_pattern_ops);
 6   DROP INDEX public.anagrafica_sede_nome_b7509597_like;
       public         postgres    false    205            �           1259    121451 "   anagrafica_sede_slug_45022f7a_like    INDEX     k   CREATE INDEX anagrafica_sede_slug_45022f7a_like ON anagrafica_sede USING btree (slug varchar_pattern_ops);
 6   DROP INDEX public.anagrafica_sede_slug_45022f7a_like;
       public         postgres    false    205            �           1259    121452 "   anagrafica_sede_tipo_6828be71_like    INDEX     k   CREATE INDEX anagrafica_sede_tipo_6828be71_like ON anagrafica_sede USING btree (tipo varchar_pattern_ops);
 6   DROP INDEX public.anagrafica_sede_tipo_6828be71_like;
       public         postgres    false    205            �           1259    121453    anagrafica_telefono_36063dc9    INDEX     Z   CREATE INDEX anagrafica_telefono_36063dc9 ON anagrafica_telefono USING btree (creazione);
 0   DROP INDEX public.anagrafica_telefono_36063dc9;
       public         postgres    false    207            �           1259    121454    anagrafica_telefono_69bd2e5f    INDEX     `   CREATE INDEX anagrafica_telefono_69bd2e5f ON anagrafica_telefono USING btree (ultima_modifica);
 0   DROP INDEX public.anagrafica_telefono_69bd2e5f;
       public         postgres    false    207            �           1259    121455    anagrafica_telefono_e8589820    INDEX     [   CREATE INDEX anagrafica_telefono_e8589820 ON anagrafica_telefono USING btree (persona_id);
 0   DROP INDEX public.anagrafica_telefono_e8589820;
       public         postgres    false    207            �           1259    121456 +   anagrafica_telefono_persona_id_f331fd86_idx    INDEX     t   CREATE INDEX anagrafica_telefono_persona_id_f331fd86_idx ON anagrafica_telefono USING btree (persona_id, servizio);
 ?   DROP INDEX public.anagrafica_telefono_persona_id_f331fd86_idx;
       public         postgres    false    207    207            �           1259    121457 !   anagrafica_trasferimento_36063dc9    INDEX     d   CREATE INDEX anagrafica_trasferimento_36063dc9 ON anagrafica_trasferimento USING btree (creazione);
 5   DROP INDEX public.anagrafica_trasferimento_36063dc9;
       public         postgres    false    209            �           1259    121458 !   anagrafica_trasferimento_43662d06    INDEX     e   CREATE INDEX anagrafica_trasferimento_43662d06 ON anagrafica_trasferimento USING btree (confermata);
 5   DROP INDEX public.anagrafica_trasferimento_43662d06;
       public         postgres    false    209            �           1259    121459 !   anagrafica_trasferimento_4a9487af    INDEX     c   CREATE INDEX anagrafica_trasferimento_4a9487af ON anagrafica_trasferimento USING btree (ritirata);
 5   DROP INDEX public.anagrafica_trasferimento_4a9487af;
       public         postgres    false    209            �           1259    121460 !   anagrafica_trasferimento_530b0ac8    INDEX     j   CREATE INDEX anagrafica_trasferimento_530b0ac8 ON anagrafica_trasferimento USING btree (appartenenza_id);
 5   DROP INDEX public.anagrafica_trasferimento_530b0ac8;
       public         postgres    false    209            �           1259    121461 !   anagrafica_trasferimento_69bd2e5f    INDEX     j   CREATE INDEX anagrafica_trasferimento_69bd2e5f ON anagrafica_trasferimento USING btree (ultima_modifica);
 5   DROP INDEX public.anagrafica_trasferimento_69bd2e5f;
       public         postgres    false    209            �           1259    121462 !   anagrafica_trasferimento_cb8e6a80    INDEX     j   CREATE INDEX anagrafica_trasferimento_cb8e6a80 ON anagrafica_trasferimento USING btree (destinazione_id);
 5   DROP INDEX public.anagrafica_trasferimento_cb8e6a80;
       public         postgres    false    209            �           1259    121463 !   anagrafica_trasferimento_e3692faf    INDEX     i   CREATE INDEX anagrafica_trasferimento_e3692faf ON anagrafica_trasferimento USING btree (richiedente_id);
 5   DROP INDEX public.anagrafica_trasferimento_e3692faf;
       public         postgres    false    209            �           1259    121464 !   anagrafica_trasferimento_e8589820    INDEX     e   CREATE INDEX anagrafica_trasferimento_e8589820 ON anagrafica_trasferimento USING btree (persona_id);
 5   DROP INDEX public.anagrafica_trasferimento_e8589820;
       public         postgres    false    209            �           1259    121465    attivita_area_0687f864    INDEX     L   CREATE INDEX attivita_area_0687f864 ON attivita_area USING btree (sede_id);
 *   DROP INDEX public.attivita_area_0687f864;
       public         postgres    false    211            �           1259    121466    attivita_area_36063dc9    INDEX     N   CREATE INDEX attivita_area_36063dc9 ON attivita_area USING btree (creazione);
 *   DROP INDEX public.attivita_area_36063dc9;
       public         postgres    false    211            �           1259    121467    attivita_area_666ac576    INDEX     I   CREATE INDEX attivita_area_666ac576 ON attivita_area USING btree (nome);
 *   DROP INDEX public.attivita_area_666ac576;
       public         postgres    false    211            �           1259    121468    attivita_area_69bd2e5f    INDEX     T   CREATE INDEX attivita_area_69bd2e5f ON attivita_area USING btree (ultima_modifica);
 *   DROP INDEX public.attivita_area_69bd2e5f;
       public         postgres    false    211            �           1259    121469    attivita_area_cefdb931    INDEX     N   CREATE INDEX attivita_area_cefdb931 ON attivita_area USING btree (obiettivo);
 *   DROP INDEX public.attivita_area_cefdb931;
       public         postgres    false    211            �           1259    121470     attivita_area_nome_87de2dfa_like    INDEX     g   CREATE INDEX attivita_area_nome_87de2dfa_like ON attivita_area USING btree (nome varchar_pattern_ops);
 4   DROP INDEX public.attivita_area_nome_87de2dfa_like;
       public         postgres    false    211            �           1259    121471 "   attivita_area_sede_id_0593399b_idx    INDEX     c   CREATE INDEX attivita_area_sede_id_0593399b_idx ON attivita_area USING btree (sede_id, obiettivo);
 6   DROP INDEX public.attivita_area_sede_id_0593399b_idx;
       public         postgres    false    211    211            �           1259    121472    attivita_attivita_0687f864    INDEX     T   CREATE INDEX attivita_attivita_0687f864 ON attivita_attivita USING btree (sede_id);
 .   DROP INDEX public.attivita_attivita_0687f864;
       public         postgres    false    213            �           1259    121473    attivita_attivita_213ee482    INDEX     _   CREATE INDEX attivita_attivita_213ee482 ON attivita_attivita USING btree (centrale_operativa);
 .   DROP INDEX public.attivita_attivita_213ee482;
       public         postgres    false    213            �           1259    121474    attivita_attivita_2873ce9d    INDEX     U   CREATE INDEX attivita_attivita_2873ce9d ON attivita_attivita USING btree (apertura);
 .   DROP INDEX public.attivita_attivita_2873ce9d;
       public         postgres    false    213            �           1259    121475    attivita_attivita_29a104e3    INDEX     Y   CREATE INDEX attivita_attivita_29a104e3 ON attivita_attivita USING btree (locazione_id);
 .   DROP INDEX public.attivita_attivita_29a104e3;
       public         postgres    false    213            �           1259    121476    attivita_attivita_36063dc9    INDEX     V   CREATE INDEX attivita_attivita_36063dc9 ON attivita_attivita USING btree (creazione);
 .   DROP INDEX public.attivita_attivita_36063dc9;
       public         postgres    false    213            �           1259    121477    attivita_attivita_666ac576    INDEX     Q   CREATE INDEX attivita_attivita_666ac576 ON attivita_attivita USING btree (nome);
 .   DROP INDEX public.attivita_attivita_666ac576;
       public         postgres    false    213            �           1259    121478    attivita_attivita_69bd2e5f    INDEX     \   CREATE INDEX attivita_attivita_69bd2e5f ON attivita_attivita USING btree (ultima_modifica);
 .   DROP INDEX public.attivita_attivita_69bd2e5f;
       public         postgres    false    213            �           1259    121479 (   attivita_attivita_apertura_f026ec65_like    INDEX     w   CREATE INDEX attivita_attivita_apertura_f026ec65_like ON attivita_attivita USING btree (apertura varchar_pattern_ops);
 <   DROP INDEX public.attivita_attivita_apertura_f026ec65_like;
       public         postgres    false    213            �           1259    121480 1   attivita_attivita_centrale_operativa_179878e8_idx    INDEX        CREATE INDEX attivita_attivita_centrale_operativa_179878e8_idx ON attivita_attivita USING btree (centrale_operativa, sede_id);
 E   DROP INDEX public.attivita_attivita_centrale_operativa_179878e8_idx;
       public         postgres    false    213    213            �           1259    121481    attivita_attivita_d266de13    INDEX     T   CREATE INDEX attivita_attivita_d266de13 ON attivita_attivita USING btree (area_id);
 .   DROP INDEX public.attivita_attivita_d266de13;
       public         postgres    false    213            �           1259    121482    attivita_attivita_d6ef5c1f    INDEX     W   CREATE INDEX attivita_attivita_d6ef5c1f ON attivita_attivita USING btree (vecchio_id);
 .   DROP INDEX public.attivita_attivita_d6ef5c1f;
       public         postgres    false    213            �           1259    121483    attivita_attivita_e0b406f5    INDEX     R   CREATE INDEX attivita_attivita_e0b406f5 ON attivita_attivita USING btree (stato);
 .   DROP INDEX public.attivita_attivita_e0b406f5;
       public         postgres    false    213            �           1259    121484 ,   attivita_attivita_estensione_id_adfc324e_idx    INDEX     v   CREATE INDEX attivita_attivita_estensione_id_adfc324e_idx ON attivita_attivita USING btree (estensione_id, apertura);
 @   DROP INDEX public.attivita_attivita_estensione_id_adfc324e_idx;
       public         postgres    false    213    213            �           1259    121485    attivita_attivita_f911fd76    INDEX     Z   CREATE INDEX attivita_attivita_f911fd76 ON attivita_attivita USING btree (estensione_id);
 .   DROP INDEX public.attivita_attivita_f911fd76;
       public         postgres    false    213            �           1259    121486 $   attivita_attivita_nome_df14a3b3_like    INDEX     o   CREATE INDEX attivita_attivita_nome_df14a3b3_like ON attivita_attivita USING btree (nome varchar_pattern_ops);
 8   DROP INDEX public.attivita_attivita_nome_df14a3b3_like;
       public         postgres    false    213            �           1259    121487 &   attivita_attivita_sede_id_1bb22550_idx    INDEX     y   CREATE INDEX attivita_attivita_sede_id_1bb22550_idx ON attivita_attivita USING btree (sede_id, estensione_id, apertura);
 :   DROP INDEX public.attivita_attivita_sede_id_1bb22550_idx;
       public         postgres    false    213    213    213            �           1259    121488 &   attivita_attivita_sede_id_35b8f18e_idx    INDEX     �   CREATE INDEX attivita_attivita_sede_id_35b8f18e_idx ON attivita_attivita USING btree (sede_id, estensione_id, apertura, stato);
 :   DROP INDEX public.attivita_attivita_sede_id_35b8f18e_idx;
       public         postgres    false    213    213    213    213            �           1259    121489 &   attivita_attivita_sede_id_65fe7596_idx    INDEX     v   CREATE INDEX attivita_attivita_sede_id_65fe7596_idx ON attivita_attivita USING btree (sede_id, estensione_id, stato);
 :   DROP INDEX public.attivita_attivita_sede_id_65fe7596_idx;
       public         postgres    false    213    213    213            �           1259    121490 &   attivita_attivita_sede_id_96b5dddd_idx    INDEX     o   CREATE INDEX attivita_attivita_sede_id_96b5dddd_idx ON attivita_attivita USING btree (sede_id, estensione_id);
 :   DROP INDEX public.attivita_attivita_sede_id_96b5dddd_idx;
       public         postgres    false    213    213            �           1259    121491 &   attivita_attivita_sede_id_d46ac694_idx    INDEX     j   CREATE INDEX attivita_attivita_sede_id_d46ac694_idx ON attivita_attivita USING btree (sede_id, apertura);
 :   DROP INDEX public.attivita_attivita_sede_id_d46ac694_idx;
       public         postgres    false    213    213            �           1259    121492 %   attivita_attivita_stato_8003dc3a_like    INDEX     q   CREATE INDEX attivita_attivita_stato_8003dc3a_like ON attivita_attivita USING btree (stato varchar_pattern_ops);
 9   DROP INDEX public.attivita_attivita_stato_8003dc3a_like;
       public         postgres    false    213            �           1259    121493     attivita_partecipazione_177cb605    INDEX     a   CREATE INDEX attivita_partecipazione_177cb605 ON attivita_partecipazione USING btree (turno_id);
 4   DROP INDEX public.attivita_partecipazione_177cb605;
       public         postgres    false    215            �           1259    121494     attivita_partecipazione_213ee482    INDEX     k   CREATE INDEX attivita_partecipazione_213ee482 ON attivita_partecipazione USING btree (centrale_operativa);
 4   DROP INDEX public.attivita_partecipazione_213ee482;
       public         postgres    false    215            �           1259    121495     attivita_partecipazione_36063dc9    INDEX     b   CREATE INDEX attivita_partecipazione_36063dc9 ON attivita_partecipazione USING btree (creazione);
 4   DROP INDEX public.attivita_partecipazione_36063dc9;
       public         postgres    false    215            �           1259    121496     attivita_partecipazione_43662d06    INDEX     c   CREATE INDEX attivita_partecipazione_43662d06 ON attivita_partecipazione USING btree (confermata);
 4   DROP INDEX public.attivita_partecipazione_43662d06;
       public         postgres    false    215            �           1259    121497     attivita_partecipazione_4a9487af    INDEX     a   CREATE INDEX attivita_partecipazione_4a9487af ON attivita_partecipazione USING btree (ritirata);
 4   DROP INDEX public.attivita_partecipazione_4a9487af;
       public         postgres    false    215            �           1259    121498     attivita_partecipazione_69bd2e5f    INDEX     h   CREATE INDEX attivita_partecipazione_69bd2e5f ON attivita_partecipazione USING btree (ultima_modifica);
 4   DROP INDEX public.attivita_partecipazione_69bd2e5f;
       public         postgres    false    215            �           1259    121499     attivita_partecipazione_e0b406f5    INDEX     ^   CREATE INDEX attivita_partecipazione_e0b406f5 ON attivita_partecipazione USING btree (stato);
 4   DROP INDEX public.attivita_partecipazione_e0b406f5;
       public         postgres    false    215            �           1259    121500     attivita_partecipazione_e8589820    INDEX     c   CREATE INDEX attivita_partecipazione_e8589820 ON attivita_partecipazione USING btree (persona_id);
 4   DROP INDEX public.attivita_partecipazione_e8589820;
       public         postgres    false    215            �           1259    121501 /   attivita_partecipazione_persona_id_0b1793b6_idx    INDEX     �   CREATE INDEX attivita_partecipazione_persona_id_0b1793b6_idx ON attivita_partecipazione USING btree (persona_id, turno_id, stato);
 C   DROP INDEX public.attivita_partecipazione_persona_id_0b1793b6_idx;
       public         postgres    false    215    215    215            �           1259    121502 /   attivita_partecipazione_persona_id_f056b983_idx    INDEX     |   CREATE INDEX attivita_partecipazione_persona_id_f056b983_idx ON attivita_partecipazione USING btree (persona_id, turno_id);
 C   DROP INDEX public.attivita_partecipazione_persona_id_f056b983_idx;
       public         postgres    false    215    215            �           1259    121503 +   attivita_partecipazione_stato_e872ecd9_like    INDEX     }   CREATE INDEX attivita_partecipazione_stato_e872ecd9_like ON attivita_partecipazione USING btree (stato varchar_pattern_ops);
 ?   DROP INDEX public.attivita_partecipazione_stato_e872ecd9_like;
       public         postgres    false    215            �           1259    121504 -   attivita_partecipazione_turno_id_820c154b_idx    INDEX     u   CREATE INDEX attivita_partecipazione_turno_id_820c154b_idx ON attivita_partecipazione USING btree (turno_id, stato);
 A   DROP INDEX public.attivita_partecipazione_turno_id_820c154b_idx;
       public         postgres    false    215    215            �           1259    121505    attivita_turno_36063dc9    INDEX     P   CREATE INDEX attivita_turno_36063dc9 ON attivita_turno USING btree (creazione);
 +   DROP INDEX public.attivita_turno_36063dc9;
       public         postgres    false    217            �           1259    121506    attivita_turno_3abe1833    INDEX     R   CREATE INDEX attivita_turno_3abe1833 ON attivita_turno USING btree (attivita_id);
 +   DROP INDEX public.attivita_turno_3abe1833;
       public         postgres    false    217            �           1259    121507    attivita_turno_666ac576    INDEX     K   CREATE INDEX attivita_turno_666ac576 ON attivita_turno USING btree (nome);
 +   DROP INDEX public.attivita_turno_666ac576;
       public         postgres    false    217            �           1259    121508    attivita_turno_69bd2e5f    INDEX     V   CREATE INDEX attivita_turno_69bd2e5f ON attivita_turno USING btree (ultima_modifica);
 +   DROP INDEX public.attivita_turno_69bd2e5f;
       public         postgres    false    217            �           1259    121509    attivita_turno_7df656af    INDEX     M   CREATE INDEX attivita_turno_7df656af ON attivita_turno USING btree (inizio);
 +   DROP INDEX public.attivita_turno_7df656af;
       public         postgres    false    217            �           1259    121510    attivita_turno_8cac5ac4    INDEX     N   CREATE INDEX attivita_turno_8cac5ac4 ON attivita_turno USING btree (massimo);
 +   DROP INDEX public.attivita_turno_8cac5ac4;
       public         postgres    false    217            �           1259    121511    attivita_turno_9b1d5224    INDEX     S   CREATE INDEX attivita_turno_9b1d5224 ON attivita_turno USING btree (prenotazione);
 +   DROP INDEX public.attivita_turno_9b1d5224;
       public         postgres    false    217            �           1259    121512 '   attivita_turno_attivita_id_64dfe525_idx    INDEX     j   CREATE INDEX attivita_turno_attivita_id_64dfe525_idx ON attivita_turno USING btree (attivita_id, inizio);
 ;   DROP INDEX public.attivita_turno_attivita_id_64dfe525_idx;
       public         postgres    false    217    217            �           1259    121513 '   attivita_turno_attivita_id_d9f6d0b8_idx    INDEX     p   CREATE INDEX attivita_turno_attivita_id_d9f6d0b8_idx ON attivita_turno USING btree (attivita_id, inizio, fine);
 ;   DROP INDEX public.attivita_turno_attivita_id_d9f6d0b8_idx;
       public         postgres    false    217    217    217                        1259    121514    attivita_turno_bf5f7974    INDEX     M   CREATE INDEX attivita_turno_bf5f7974 ON attivita_turno USING btree (minimo);
 +   DROP INDEX public.attivita_turno_bf5f7974;
       public         postgres    false    217                       1259    121515    attivita_turno_fff25994    INDEX     K   CREATE INDEX attivita_turno_fff25994 ON attivita_turno USING btree (fine);
 +   DROP INDEX public.attivita_turno_fff25994;
       public         postgres    false    217                       1259    121516 "   attivita_turno_inizio_4ea3f755_idx    INDEX     ^   CREATE INDEX attivita_turno_inizio_4ea3f755_idx ON attivita_turno USING btree (inizio, fine);
 6   DROP INDEX public.attivita_turno_inizio_4ea3f755_idx;
       public         postgres    false    217    217                       1259    121517 !   attivita_turno_nome_3c326217_like    INDEX     i   CREATE INDEX attivita_turno_nome_3c326217_like ON attivita_turno USING btree (nome varchar_pattern_ops);
 5   DROP INDEX public.attivita_turno_nome_3c326217_like;
       public         postgres    false    217                       1259    121518    autenticazione_utenza_36063dc9    INDEX     ^   CREATE INDEX autenticazione_utenza_36063dc9 ON autenticazione_utenza USING btree (creazione);
 2   DROP INDEX public.autenticazione_utenza_36063dc9;
       public         postgres    false    219                       1259    121519    autenticazione_utenza_69bd2e5f    INDEX     d   CREATE INDEX autenticazione_utenza_69bd2e5f ON autenticazione_utenza USING btree (ultima_modifica);
 2   DROP INDEX public.autenticazione_utenza_69bd2e5f;
       public         postgres    false    219                       1259    121520 )   autenticazione_utenza_email_1427a4ce_like    INDEX     y   CREATE INDEX autenticazione_utenza_email_1427a4ce_like ON autenticazione_utenza USING btree (email varchar_pattern_ops);
 =   DROP INDEX public.autenticazione_utenza_email_1427a4ce_like;
       public         postgres    false    219                       1259    121521 %   autenticazione_utenza_groups_0e939a4f    INDEX     k   CREATE INDEX autenticazione_utenza_groups_0e939a4f ON autenticazione_utenza_groups USING btree (group_id);
 9   DROP INDEX public.autenticazione_utenza_groups_0e939a4f;
       public         postgres    false    220                       1259    121522 %   autenticazione_utenza_groups_677a0914    INDEX     l   CREATE INDEX autenticazione_utenza_groups_677a0914 ON autenticazione_utenza_groups USING btree (utenza_id);
 9   DROP INDEX public.autenticazione_utenza_groups_677a0914;
       public         postgres    false    220                       1259    121523 /   autenticazione_utenza_user_permissions_677a0914    INDEX     �   CREATE INDEX autenticazione_utenza_user_permissions_677a0914 ON autenticazione_utenza_user_permissions USING btree (utenza_id);
 C   DROP INDEX public.autenticazione_utenza_user_permissions_677a0914;
       public         postgres    false    223                       1259    121524 /   autenticazione_utenza_user_permissions_8373b171    INDEX     �   CREATE INDEX autenticazione_utenza_user_permissions_8373b171 ON autenticazione_utenza_user_permissions USING btree (permission_id);
 C   DROP INDEX public.autenticazione_utenza_user_permissions_8373b171;
       public         postgres    false    223                       1259    121525    auth_group_name_a6ea08ec_like    INDEX     a   CREATE INDEX auth_group_name_a6ea08ec_like ON auth_group USING btree (name varchar_pattern_ops);
 1   DROP INDEX public.auth_group_name_a6ea08ec_like;
       public         postgres    false    225                        1259    121526    auth_group_permissions_0e939a4f    INDEX     _   CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);
 3   DROP INDEX public.auth_group_permissions_0e939a4f;
       public         postgres    false    227            !           1259    121527    auth_group_permissions_8373b171    INDEX     d   CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);
 3   DROP INDEX public.auth_group_permissions_8373b171;
       public         postgres    false    227            &           1259    121528    auth_permission_417f1b1c    INDEX     X   CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);
 ,   DROP INDEX public.auth_permission_417f1b1c;
       public         postgres    false    229            +           1259    121529    base_allegato_36063dc9    INDEX     N   CREATE INDEX base_allegato_36063dc9 ON base_allegato USING btree (creazione);
 *   DROP INDEX public.base_allegato_36063dc9;
       public         postgres    false    231            ,           1259    121530    base_allegato_69bd2e5f    INDEX     T   CREATE INDEX base_allegato_69bd2e5f ON base_allegato USING btree (ultima_modifica);
 *   DROP INDEX public.base_allegato_69bd2e5f;
       public         postgres    false    231            -           1259    121531    base_allegato_9c82ce86    INDEX     O   CREATE INDEX base_allegato_9c82ce86 ON base_allegato USING btree (oggetto_id);
 *   DROP INDEX public.base_allegato_9c82ce86;
       public         postgres    false    231            .           1259    121532    base_allegato_f5148848    INDEX     M   CREATE INDEX base_allegato_f5148848 ON base_allegato USING btree (scadenza);
 *   DROP INDEX public.base_allegato_f5148848;
       public         postgres    false    231            /           1259    121533    base_allegato_fe2a0979    INDEX     T   CREATE INDEX base_allegato_fe2a0979 ON base_allegato USING btree (oggetto_tipo_id);
 *   DROP INDEX public.base_allegato_fe2a0979;
       public         postgres    false    231            2           1259    121534    base_autorizzazione_1d6d29b9    INDEX     h   CREATE INDEX base_autorizzazione_1d6d29b9 ON base_autorizzazione USING btree (destinatario_oggetto_id);
 0   DROP INDEX public.base_autorizzazione_1d6d29b9;
       public         postgres    false    233            3           1259    121535    base_autorizzazione_2fe19435    INDEX     [   CREATE INDEX base_autorizzazione_2fe19435 ON base_autorizzazione USING btree (necessaria);
 0   DROP INDEX public.base_autorizzazione_2fe19435;
       public         postgres    false    233            4           1259    121536    base_autorizzazione_36063dc9    INDEX     Z   CREATE INDEX base_autorizzazione_36063dc9 ON base_autorizzazione USING btree (creazione);
 0   DROP INDEX public.base_autorizzazione_36063dc9;
       public         postgres    false    233            5           1259    121537    base_autorizzazione_515fa17e    INDEX     ^   CREATE INDEX base_autorizzazione_515fa17e ON base_autorizzazione USING btree (firmatario_id);
 0   DROP INDEX public.base_autorizzazione_515fa17e;
       public         postgres    false    233            6           1259    121538    base_autorizzazione_69bd2e5f    INDEX     `   CREATE INDEX base_autorizzazione_69bd2e5f ON base_autorizzazione USING btree (ultima_modifica);
 0   DROP INDEX public.base_autorizzazione_69bd2e5f;
       public         postgres    false    233            7           1259    121539    base_autorizzazione_9c82ce86    INDEX     [   CREATE INDEX base_autorizzazione_9c82ce86 ON base_autorizzazione USING btree (oggetto_id);
 0   DROP INDEX public.base_autorizzazione_9c82ce86;
       public         postgres    false    233            8           1259    121540    base_autorizzazione_9fd792c4    INDEX     Y   CREATE INDEX base_autorizzazione_9fd792c4 ON base_autorizzazione USING btree (concessa);
 0   DROP INDEX public.base_autorizzazione_9fd792c4;
       public         postgres    false    233            9           1259    121541    base_autorizzazione_c836c01f    INDEX     m   CREATE INDEX base_autorizzazione_c836c01f ON base_autorizzazione USING btree (destinatario_oggetto_tipo_id);
 0   DROP INDEX public.base_autorizzazione_c836c01f;
       public         postgres    false    233            :           1259    121542 =   base_autorizzazione_destinatario_oggetto_tipo_id_13cef3d7_idx    INDEX     �   CREATE INDEX base_autorizzazione_destinatario_oggetto_tipo_id_13cef3d7_idx ON base_autorizzazione USING btree (destinatario_oggetto_tipo_id, destinatario_oggetto_id);
 Q   DROP INDEX public.base_autorizzazione_destinatario_oggetto_tipo_id_13cef3d7_idx;
       public         postgres    false    233    233            ;           1259    121543 4   base_autorizzazione_destinatario_ruolo_564a3afe_like    INDEX     �   CREATE INDEX base_autorizzazione_destinatario_ruolo_564a3afe_like ON base_autorizzazione USING btree (destinatario_ruolo varchar_pattern_ops);
 H   DROP INDEX public.base_autorizzazione_destinatario_ruolo_564a3afe_like;
       public         postgres    false    233            <           1259    121544 4   base_autorizzazione_destinatario_ruolo_564a3afe_uniq    INDEX     {   CREATE INDEX base_autorizzazione_destinatario_ruolo_564a3afe_uniq ON base_autorizzazione USING btree (destinatario_ruolo);
 H   DROP INDEX public.base_autorizzazione_destinatario_ruolo_564a3afe_uniq;
       public         postgres    false    233            =           1259    121545 3   base_autorizzazione_destinatario_ruolo_67040295_idx    INDEX     �   CREATE INDEX base_autorizzazione_destinatario_ruolo_67040295_idx ON base_autorizzazione USING btree (destinatario_ruolo, destinatario_oggetto_tipo_id);
 G   DROP INDEX public.base_autorizzazione_destinatario_ruolo_67040295_idx;
       public         postgres    false    233    233            >           1259    121546 3   base_autorizzazione_destinatario_ruolo_9918e77c_idx    INDEX     �   CREATE INDEX base_autorizzazione_destinatario_ruolo_9918e77c_idx ON base_autorizzazione USING btree (destinatario_ruolo, destinatario_oggetto_tipo_id, destinatario_oggetto_id);
 G   DROP INDEX public.base_autorizzazione_destinatario_ruolo_9918e77c_idx;
       public         postgres    false    233    233    233            ?           1259    121547    base_autorizzazione_e3692faf    INDEX     _   CREATE INDEX base_autorizzazione_e3692faf ON base_autorizzazione USING btree (richiedente_id);
 0   DROP INDEX public.base_autorizzazione_e3692faf;
       public         postgres    false    233            @           1259    121548    base_autorizzazione_fe2a0979    INDEX     `   CREATE INDEX base_autorizzazione_fe2a0979 ON base_autorizzazione USING btree (oggetto_tipo_id);
 0   DROP INDEX public.base_autorizzazione_fe2a0979;
       public         postgres    false    233            A           1259    121549 +   base_autorizzazione_necessaria_1186765f_idx    INDEX     �   CREATE INDEX base_autorizzazione_necessaria_1186765f_idx ON base_autorizzazione USING btree (necessaria, destinatario_oggetto_tipo_id, destinatario_oggetto_id);
 ?   DROP INDEX public.base_autorizzazione_necessaria_1186765f_idx;
       public         postgres    false    233    233    233            B           1259    121550 +   base_autorizzazione_necessaria_29c8dc15_idx    INDEX     t   CREATE INDEX base_autorizzazione_necessaria_29c8dc15_idx ON base_autorizzazione USING btree (necessaria, concessa);
 ?   DROP INDEX public.base_autorizzazione_necessaria_29c8dc15_idx;
       public         postgres    false    233    233            C           1259    121551 +   base_autorizzazione_necessaria_34dab438_idx    INDEX     �   CREATE INDEX base_autorizzazione_necessaria_34dab438_idx ON base_autorizzazione USING btree (necessaria, destinatario_ruolo, destinatario_oggetto_tipo_id, destinatario_oggetto_id);
 ?   DROP INDEX public.base_autorizzazione_necessaria_34dab438_idx;
       public         postgres    false    233    233    233    233            D           1259    121552 +   base_autorizzazione_necessaria_c3d12f99_idx    INDEX     w   CREATE INDEX base_autorizzazione_necessaria_c3d12f99_idx ON base_autorizzazione USING btree (necessaria, progressivo);
 ?   DROP INDEX public.base_autorizzazione_necessaria_c3d12f99_idx;
       public         postgres    false    233    233            G           1259    121553    base_locazione_16a74f32    INDEX     P   CREATE INDEX base_locazione_16a74f32 ON base_locazione USING btree (provincia);
 +   DROP INDEX public.base_locazione_16a74f32;
       public         postgres    false    235            H           1259    121554    base_locazione_36063dc9    INDEX     P   CREATE INDEX base_locazione_36063dc9 ON base_locazione USING btree (creazione);
 +   DROP INDEX public.base_locazione_36063dc9;
       public         postgres    false    235            I           1259    121555    base_locazione_3d791e43    INDEX     J   CREATE INDEX base_locazione_3d791e43 ON base_locazione USING btree (cap);
 +   DROP INDEX public.base_locazione_3d791e43;
       public         postgres    false    235            J           1259    121556    base_locazione_5d3c7293    INDEX     N   CREATE INDEX base_locazione_5d3c7293 ON base_locazione USING btree (regione);
 +   DROP INDEX public.base_locazione_5d3c7293;
       public         postgres    false    235            K           1259    121557    base_locazione_69bd2e5f    INDEX     V   CREATE INDEX base_locazione_69bd2e5f ON base_locazione USING btree (ultima_modifica);
 +   DROP INDEX public.base_locazione_69bd2e5f;
       public         postgres    false    235            L           1259    121558    base_locazione_800d4d10    INDEX     M   CREATE INDEX base_locazione_800d4d10 ON base_locazione USING btree (comune);
 +   DROP INDEX public.base_locazione_800d4d10;
       public         postgres    false    235            M           1259    121559     base_locazione_cap_3ebdebe3_like    INDEX     g   CREATE INDEX base_locazione_cap_3ebdebe3_like ON base_locazione USING btree (cap varchar_pattern_ops);
 4   DROP INDEX public.base_locazione_cap_3ebdebe3_like;
       public         postgres    false    235            N           1259    121560 #   base_locazione_comune_9aebb52b_like    INDEX     m   CREATE INDEX base_locazione_comune_9aebb52b_like ON base_locazione USING btree (comune varchar_pattern_ops);
 7   DROP INDEX public.base_locazione_comune_9aebb52b_like;
       public         postgres    false    235            O           1259    121561     base_locazione_geo_2fecf11f_uniq    INDEX     S   CREATE INDEX base_locazione_geo_2fecf11f_uniq ON base_locazione USING btree (geo);
 4   DROP INDEX public.base_locazione_geo_2fecf11f_uniq;
       public         postgres    false    235    2    2    8    2    2    8    8    2    8    2    8    2    8    2    8    2    8    2    8    8            P           1259    121562    base_locazione_geo_id    INDEX     G   CREATE INDEX base_locazione_geo_id ON base_locazione USING gist (geo);
 )   DROP INDEX public.base_locazione_geo_id;
       public         postgres    false    2    8    2    2    8    8    2    8    2    8    2    8    2    8    2    8    2    8    2    8    2    2    8    8    2    8    235            Q           1259    121563 &   base_locazione_indirizzo_5aee5061_like    INDEX     s   CREATE INDEX base_locazione_indirizzo_5aee5061_like ON base_locazione USING btree (indirizzo varchar_pattern_ops);
 :   DROP INDEX public.base_locazione_indirizzo_5aee5061_like;
       public         postgres    false    235            V           1259    121564 &   base_locazione_provincia_8aed40a7_like    INDEX     s   CREATE INDEX base_locazione_provincia_8aed40a7_like ON base_locazione USING btree (provincia varchar_pattern_ops);
 :   DROP INDEX public.base_locazione_provincia_8aed40a7_like;
       public         postgres    false    235            W           1259    121565 $   base_locazione_regione_da2c3801_like    INDEX     o   CREATE INDEX base_locazione_regione_da2c3801_like ON base_locazione USING btree (regione varchar_pattern_ops);
 8   DROP INDEX public.base_locazione_regione_da2c3801_like;
       public         postgres    false    235            X           1259    121566    base_log_01b9b886    INDEX     L   CREATE INDEX base_log_01b9b886 ON base_log USING btree (oggetto_app_label);
 %   DROP INDEX public.base_log_01b9b886;
       public         postgres    false    237            Y           1259    121567    base_log_36063dc9    INDEX     D   CREATE INDEX base_log_36063dc9 ON base_log USING btree (creazione);
 %   DROP INDEX public.base_log_36063dc9;
       public         postgres    false    237            Z           1259    121568    base_log_419c0abe    INDEX     E   CREATE INDEX base_log_419c0abe ON base_log USING btree (oggetto_pk);
 %   DROP INDEX public.base_log_419c0abe;
       public         postgres    false    237            [           1259    121569    base_log_69bd2e5f    INDEX     J   CREATE INDEX base_log_69bd2e5f ON base_log USING btree (ultima_modifica);
 %   DROP INDEX public.base_log_69bd2e5f;
       public         postgres    false    237            \           1259    121570    base_log_76c74769    INDEX     H   CREATE INDEX base_log_76c74769 ON base_log USING btree (oggetto_campo);
 %   DROP INDEX public.base_log_76c74769;
       public         postgres    false    237            ]           1259    121571    base_log_af04014c    INDEX     H   CREATE INDEX base_log_af04014c ON base_log USING btree (oggetto_model);
 %   DROP INDEX public.base_log_af04014c;
       public         postgres    false    237            ^           1259    121572    base_log_e8589820    INDEX     E   CREATE INDEX base_log_e8589820 ON base_log USING btree (persona_id);
 %   DROP INDEX public.base_log_e8589820;
       public         postgres    false    237            _           1259    121573 (   base_log_oggetto_app_label_ab1437f7_like    INDEX     w   CREATE INDEX base_log_oggetto_app_label_ab1437f7_like ON base_log USING btree (oggetto_app_label varchar_pattern_ops);
 <   DROP INDEX public.base_log_oggetto_app_label_ab1437f7_like;
       public         postgres    false    237            `           1259    121574 $   base_log_oggetto_campo_dc04c832_like    INDEX     o   CREATE INDEX base_log_oggetto_campo_dc04c832_like ON base_log USING btree (oggetto_campo varchar_pattern_ops);
 8   DROP INDEX public.base_log_oggetto_campo_dc04c832_like;
       public         postgres    false    237            a           1259    121575 $   base_log_oggetto_model_482bbd90_like    INDEX     o   CREATE INDEX base_log_oggetto_model_482bbd90_like ON base_log USING btree (oggetto_model varchar_pattern_ops);
 8   DROP INDEX public.base_log_oggetto_model_482bbd90_like;
       public         postgres    false    237            d           1259    121576    base_token_36063dc9    INDEX     H   CREATE INDEX base_token_36063dc9 ON base_token USING btree (creazione);
 '   DROP INDEX public.base_token_36063dc9;
       public         postgres    false    239            e           1259    121577    base_token_69bd2e5f    INDEX     N   CREATE INDEX base_token_69bd2e5f ON base_token USING btree (ultima_modifica);
 '   DROP INDEX public.base_token_69bd2e5f;
       public         postgres    false    239            h           1259    121578    base_token_e8589820    INDEX     I   CREATE INDEX base_token_e8589820 ON base_token USING btree (persona_id);
 '   DROP INDEX public.base_token_e8589820;
       public         postgres    false    239            i           1259    121579    base_token_f17ca2c8    INDEX     G   CREATE INDEX base_token_f17ca2c8 ON base_token USING btree (redirect);
 '   DROP INDEX public.base_token_f17ca2c8;
       public         postgres    false    239            l           1259    121580 (   centrale_operativa_reperibilita_36063dc9    INDEX     r   CREATE INDEX centrale_operativa_reperibilita_36063dc9 ON centrale_operativa_reperibilita USING btree (creazione);
 <   DROP INDEX public.centrale_operativa_reperibilita_36063dc9;
       public         postgres    false    241            m           1259    121581 (   centrale_operativa_reperibilita_69bd2e5f    INDEX     x   CREATE INDEX centrale_operativa_reperibilita_69bd2e5f ON centrale_operativa_reperibilita USING btree (ultima_modifica);
 <   DROP INDEX public.centrale_operativa_reperibilita_69bd2e5f;
       public         postgres    false    241            n           1259    121582 (   centrale_operativa_reperibilita_7df656af    INDEX     o   CREATE INDEX centrale_operativa_reperibilita_7df656af ON centrale_operativa_reperibilita USING btree (inizio);
 <   DROP INDEX public.centrale_operativa_reperibilita_7df656af;
       public         postgres    false    241            o           1259    121583 (   centrale_operativa_reperibilita_e8589820    INDEX     s   CREATE INDEX centrale_operativa_reperibilita_e8589820 ON centrale_operativa_reperibilita USING btree (persona_id);
 <   DROP INDEX public.centrale_operativa_reperibilita_e8589820;
       public         postgres    false    241            p           1259    121584 (   centrale_operativa_reperibilita_fff25994    INDEX     m   CREATE INDEX centrale_operativa_reperibilita_fff25994 ON centrale_operativa_reperibilita USING btree (fine);
 <   DROP INDEX public.centrale_operativa_reperibilita_fff25994;
       public         postgres    false    241            s           1259    121585 !   centrale_operativa_turno_177cb605    INDEX     c   CREATE INDEX centrale_operativa_turno_177cb605 ON centrale_operativa_turno USING btree (turno_id);
 5   DROP INDEX public.centrale_operativa_turno_177cb605;
       public         postgres    false    243            t           1259    121586 !   centrale_operativa_turno_36063dc9    INDEX     d   CREATE INDEX centrale_operativa_turno_36063dc9 ON centrale_operativa_turno USING btree (creazione);
 5   DROP INDEX public.centrale_operativa_turno_36063dc9;
       public         postgres    false    243            u           1259    121587 !   centrale_operativa_turno_69bd2e5f    INDEX     j   CREATE INDEX centrale_operativa_turno_69bd2e5f ON centrale_operativa_turno USING btree (ultima_modifica);
 5   DROP INDEX public.centrale_operativa_turno_69bd2e5f;
       public         postgres    false    243            v           1259    121588 !   centrale_operativa_turno_aa815821    INDEX     i   CREATE INDEX centrale_operativa_turno_aa815821 ON centrale_operativa_turno USING btree (smontato_da_id);
 5   DROP INDEX public.centrale_operativa_turno_aa815821;
       public         postgres    false    243            w           1259    121589 !   centrale_operativa_turno_cf57b80f    INDEX     h   CREATE INDEX centrale_operativa_turno_cf57b80f ON centrale_operativa_turno USING btree (montato_da_id);
 5   DROP INDEX public.centrale_operativa_turno_cf57b80f;
       public         postgres    false    243            x           1259    121590 !   centrale_operativa_turno_e8589820    INDEX     e   CREATE INDEX centrale_operativa_turno_e8589820 ON centrale_operativa_turno USING btree (persona_id);
 5   DROP INDEX public.centrale_operativa_turno_e8589820;
       public         postgres    false    243            y           1259    121591 0   centrale_operativa_turno_persona_id_3410fbc6_idx    INDEX     ~   CREATE INDEX centrale_operativa_turno_persona_id_3410fbc6_idx ON centrale_operativa_turno USING btree (persona_id, turno_id);
 D   DROP INDEX public.centrale_operativa_turno_persona_id_3410fbc6_idx;
       public         postgres    false    243    243            |           1259    121592    curriculum_titolo_401281b0    INDEX     Q   CREATE INDEX curriculum_titolo_401281b0 ON curriculum_titolo USING btree (tipo);
 .   DROP INDEX public.curriculum_titolo_401281b0;
       public         postgres    false    245            }           1259    121593    curriculum_titolo_666ac576    INDEX     Q   CREATE INDEX curriculum_titolo_666ac576 ON curriculum_titolo USING btree (nome);
 .   DROP INDEX public.curriculum_titolo_666ac576;
       public         postgres    false    245            ~           1259    121594    curriculum_titolo_d6ef5c1f    INDEX     W   CREATE INDEX curriculum_titolo_d6ef5c1f ON curriculum_titolo USING btree (vecchio_id);
 .   DROP INDEX public.curriculum_titolo_d6ef5c1f;
       public         postgres    false    245                       1259    121595 $   curriculum_titolo_nome_77553fbd_like    INDEX     o   CREATE INDEX curriculum_titolo_nome_77553fbd_like ON curriculum_titolo USING btree (nome varchar_pattern_ops);
 8   DROP INDEX public.curriculum_titolo_nome_77553fbd_like;
       public         postgres    false    245            �           1259    121596 $   curriculum_titolo_tipo_aafed192_like    INDEX     o   CREATE INDEX curriculum_titolo_tipo_aafed192_like ON curriculum_titolo USING btree (tipo varchar_pattern_ops);
 8   DROP INDEX public.curriculum_titolo_tipo_aafed192_like;
       public         postgres    false    245            �           1259    121597 #   curriculum_titolopersonale_36063dc9    INDEX     h   CREATE INDEX curriculum_titolopersonale_36063dc9 ON curriculum_titolopersonale USING btree (creazione);
 7   DROP INDEX public.curriculum_titolopersonale_36063dc9;
       public         postgres    false    247            �           1259    121598 #   curriculum_titolopersonale_43662d06    INDEX     i   CREATE INDEX curriculum_titolopersonale_43662d06 ON curriculum_titolopersonale USING btree (confermata);
 7   DROP INDEX public.curriculum_titolopersonale_43662d06;
       public         postgres    false    247            �           1259    121599 #   curriculum_titolopersonale_4a9487af    INDEX     g   CREATE INDEX curriculum_titolopersonale_4a9487af ON curriculum_titolopersonale USING btree (ritirata);
 7   DROP INDEX public.curriculum_titolopersonale_4a9487af;
       public         postgres    false    247            �           1259    121600 #   curriculum_titolopersonale_5cd09f51    INDEX     k   CREATE INDEX curriculum_titolopersonale_5cd09f51 ON curriculum_titolopersonale USING btree (codice_corso);
 7   DROP INDEX public.curriculum_titolopersonale_5cd09f51;
       public         postgres    false    247            �           1259    121601 #   curriculum_titolopersonale_69bd2e5f    INDEX     n   CREATE INDEX curriculum_titolopersonale_69bd2e5f ON curriculum_titolopersonale USING btree (ultima_modifica);
 7   DROP INDEX public.curriculum_titolopersonale_69bd2e5f;
       public         postgres    false    247            �           1259    121602 #   curriculum_titolopersonale_a4c17435    INDEX     p   CREATE INDEX curriculum_titolopersonale_a4c17435 ON curriculum_titolopersonale USING btree (certificato_da_id);
 7   DROP INDEX public.curriculum_titolopersonale_a4c17435;
       public         postgres    false    247            �           1259    121603 /   curriculum_titolopersonale_codice_b6ced81c_like    INDEX     �   CREATE INDEX curriculum_titolopersonale_codice_b6ced81c_like ON curriculum_titolopersonale USING btree (codice varchar_pattern_ops);
 C   DROP INDEX public.curriculum_titolopersonale_codice_b6ced81c_like;
       public         postgres    false    247            �           1259    121604 5   curriculum_titolopersonale_codice_corso_d680009e_like    INDEX     �   CREATE INDEX curriculum_titolopersonale_codice_corso_d680009e_like ON curriculum_titolopersonale USING btree (codice_corso varchar_pattern_ops);
 I   DROP INDEX public.curriculum_titolopersonale_codice_corso_d680009e_like;
       public         postgres    false    247            �           1259    121605 #   curriculum_titolopersonale_df36e023    INDEX     h   CREATE INDEX curriculum_titolopersonale_df36e023 ON curriculum_titolopersonale USING btree (titolo_id);
 7   DROP INDEX public.curriculum_titolopersonale_df36e023;
       public         postgres    false    247            �           1259    121606 #   curriculum_titolopersonale_df5c2c5c    INDEX     e   CREATE INDEX curriculum_titolopersonale_df5c2c5c ON curriculum_titolopersonale USING btree (codice);
 7   DROP INDEX public.curriculum_titolopersonale_df5c2c5c;
       public         postgres    false    247            �           1259    121607 #   curriculum_titolopersonale_e8589820    INDEX     i   CREATE INDEX curriculum_titolopersonale_e8589820 ON curriculum_titolopersonale USING btree (persona_id);
 7   DROP INDEX public.curriculum_titolopersonale_e8589820;
       public         postgres    false    247            �           1259    121608    django_admin_log_417f1b1c    INDEX     Z   CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);
 -   DROP INDEX public.django_admin_log_417f1b1c;
       public         postgres    false    249            �           1259    121609    django_admin_log_e8701ad4    INDEX     R   CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);
 -   DROP INDEX public.django_admin_log_e8701ad4;
       public         postgres    false    249            �           1259    121610    django_cron_cronjoblog_305d2889    INDEX     _   CREATE INDEX django_cron_cronjoblog_305d2889 ON django_cron_cronjoblog USING btree (end_time);
 3   DROP INDEX public.django_cron_cronjoblog_305d2889;
       public         postgres    false    253            �           1259    121611    django_cron_cronjoblog_a05e4b70    INDEX     b   CREATE INDEX django_cron_cronjoblog_a05e4b70 ON django_cron_cronjoblog USING btree (ran_at_time);
 3   DROP INDEX public.django_cron_cronjoblog_a05e4b70;
       public         postgres    false    253            �           1259    121612    django_cron_cronjoblog_c1336794    INDEX     [   CREATE INDEX django_cron_cronjoblog_c1336794 ON django_cron_cronjoblog USING btree (code);
 3   DROP INDEX public.django_cron_cronjoblog_c1336794;
       public         postgres    false    253            �           1259    121613    django_cron_cronjoblog_c4d98dbd    INDEX     a   CREATE INDEX django_cron_cronjoblog_c4d98dbd ON django_cron_cronjoblog USING btree (start_time);
 3   DROP INDEX public.django_cron_cronjoblog_c4d98dbd;
       public         postgres    false    253            �           1259    121614 )   django_cron_cronjoblog_code_48865653_like    INDEX     y   CREATE INDEX django_cron_cronjoblog_code_48865653_like ON django_cron_cronjoblog USING btree (code varchar_pattern_ops);
 =   DROP INDEX public.django_cron_cronjoblog_code_48865653_like;
       public         postgres    false    253            �           1259    121615 (   django_cron_cronjoblog_code_4fc78f9d_idx    INDEX     p   CREATE INDEX django_cron_cronjoblog_code_4fc78f9d_idx ON django_cron_cronjoblog USING btree (code, start_time);
 <   DROP INDEX public.django_cron_cronjoblog_code_4fc78f9d_idx;
       public         postgres    false    253    253            �           1259    121616 (   django_cron_cronjoblog_code_84da9606_idx    INDEX     }   CREATE INDEX django_cron_cronjoblog_code_84da9606_idx ON django_cron_cronjoblog USING btree (code, is_success, ran_at_time);
 <   DROP INDEX public.django_cron_cronjoblog_code_84da9606_idx;
       public         postgres    false    253    253    253            �           1259    121617 (   django_cron_cronjoblog_code_8b50b8fa_idx    INDEX     }   CREATE INDEX django_cron_cronjoblog_code_8b50b8fa_idx ON django_cron_cronjoblog USING btree (code, start_time, ran_at_time);
 <   DROP INDEX public.django_cron_cronjoblog_code_8b50b8fa_idx;
       public         postgres    false    253    253    253            �           1259    121618    django_session_de54fa62    INDEX     R   CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);
 +   DROP INDEX public.django_session_de54fa62;
       public         postgres    false    257            �           1259    121619 (   django_session_session_key_c0390e0f_like    INDEX     w   CREATE INDEX django_session_session_key_c0390e0f_like ON django_session USING btree (session_key varchar_pattern_ops);
 <   DROP INDEX public.django_session_session_key_c0390e0f_like;
       public         postgres    false    257            �           1259    121620     django_site_domain_a2e37b91_like    INDEX     g   CREATE INDEX django_site_domain_a2e37b91_like ON django_site USING btree (domain varchar_pattern_ops);
 4   DROP INDEX public.django_site_domain_a2e37b91_like;
       public         postgres    false    258            �           1259    121621    formazione_aspirante_29a104e3    INDEX     _   CREATE INDEX formazione_aspirante_29a104e3 ON formazione_aspirante USING btree (locazione_id);
 1   DROP INDEX public.formazione_aspirante_29a104e3;
       public         postgres    false    260            �           1259    121622    formazione_aspirante_36063dc9    INDEX     \   CREATE INDEX formazione_aspirante_36063dc9 ON formazione_aspirante USING btree (creazione);
 1   DROP INDEX public.formazione_aspirante_36063dc9;
       public         postgres    false    260            �           1259    121623    formazione_aspirante_69bd2e5f    INDEX     b   CREATE INDEX formazione_aspirante_69bd2e5f ON formazione_aspirante USING btree (ultima_modifica);
 1   DROP INDEX public.formazione_aspirante_69bd2e5f;
       public         postgres    false    260            �           1259    121624 )   formazione_aspirante_raggio_1d2fe13c_uniq    INDEX     e   CREATE INDEX formazione_aspirante_raggio_1d2fe13c_uniq ON formazione_aspirante USING btree (raggio);
 =   DROP INDEX public.formazione_aspirante_raggio_1d2fe13c_uniq;
       public         postgres    false    260            �           1259    121625 $   formazione_assenzacorsobase_13c52846    INDEX     k   CREATE INDEX formazione_assenzacorsobase_13c52846 ON formazione_assenzacorsobase USING btree (lezione_id);
 8   DROP INDEX public.formazione_assenzacorsobase_13c52846;
       public         postgres    false    262            �           1259    121626 $   formazione_assenzacorsobase_36063dc9    INDEX     j   CREATE INDEX formazione_assenzacorsobase_36063dc9 ON formazione_assenzacorsobase USING btree (creazione);
 8   DROP INDEX public.formazione_assenzacorsobase_36063dc9;
       public         postgres    false    262            �           1259    121627 $   formazione_assenzacorsobase_69bd2e5f    INDEX     p   CREATE INDEX formazione_assenzacorsobase_69bd2e5f ON formazione_assenzacorsobase USING btree (ultima_modifica);
 8   DROP INDEX public.formazione_assenzacorsobase_69bd2e5f;
       public         postgres    false    262            �           1259    121628 $   formazione_assenzacorsobase_b66de96c    INDEX     q   CREATE INDEX formazione_assenzacorsobase_b66de96c ON formazione_assenzacorsobase USING btree (registrata_da_id);
 8   DROP INDEX public.formazione_assenzacorsobase_b66de96c;
       public         postgres    false    262            �           1259    121629 $   formazione_assenzacorsobase_e8589820    INDEX     k   CREATE INDEX formazione_assenzacorsobase_e8589820 ON formazione_assenzacorsobase USING btree (persona_id);
 8   DROP INDEX public.formazione_assenzacorsobase_e8589820;
       public         postgres    false    262            �           1259    121630    formazione_corsobase_0687f864    INDEX     Z   CREATE INDEX formazione_corsobase_0687f864 ON formazione_corsobase USING btree (sede_id);
 1   DROP INDEX public.formazione_corsobase_0687f864;
       public         postgres    false    264            �           1259    121631    formazione_corsobase_29a104e3    INDEX     _   CREATE INDEX formazione_corsobase_29a104e3 ON formazione_corsobase USING btree (locazione_id);
 1   DROP INDEX public.formazione_corsobase_29a104e3;
       public         postgres    false    264            �           1259    121632    formazione_corsobase_36063dc9    INDEX     \   CREATE INDEX formazione_corsobase_36063dc9 ON formazione_corsobase USING btree (creazione);
 1   DROP INDEX public.formazione_corsobase_36063dc9;
       public         postgres    false    264            �           1259    121633    formazione_corsobase_69bd2e5f    INDEX     b   CREATE INDEX formazione_corsobase_69bd2e5f ON formazione_corsobase USING btree (ultima_modifica);
 1   DROP INDEX public.formazione_corsobase_69bd2e5f;
       public         postgres    false    264            �           1259    121634    formazione_corsobase_6b81ba8e    INDEX     ^   CREATE INDEX formazione_corsobase_6b81ba8e ON formazione_corsobase USING btree (progressivo);
 1   DROP INDEX public.formazione_corsobase_6b81ba8e;
       public         postgres    false    264            �           1259    121635    formazione_corsobase_d6ef5c1f    INDEX     ]   CREATE INDEX formazione_corsobase_d6ef5c1f ON formazione_corsobase USING btree (vecchio_id);
 1   DROP INDEX public.formazione_corsobase_d6ef5c1f;
       public         postgres    false    264            �           1259    121636    formazione_corsobase_ddc70b20    INDEX     W   CREATE INDEX formazione_corsobase_ddc70b20 ON formazione_corsobase USING btree (anno);
 1   DROP INDEX public.formazione_corsobase_ddc70b20;
       public         postgres    false    264            �           1259    121637 $   formazione_lezionecorsobase_36063dc9    INDEX     j   CREATE INDEX formazione_lezionecorsobase_36063dc9 ON formazione_lezionecorsobase USING btree (creazione);
 8   DROP INDEX public.formazione_lezionecorsobase_36063dc9;
       public         postgres    false    266            �           1259    121638 $   formazione_lezionecorsobase_69bd2e5f    INDEX     p   CREATE INDEX formazione_lezionecorsobase_69bd2e5f ON formazione_lezionecorsobase USING btree (ultima_modifica);
 8   DROP INDEX public.formazione_lezionecorsobase_69bd2e5f;
       public         postgres    false    266            �           1259    121639 $   formazione_lezionecorsobase_7d9c2dba    INDEX     i   CREATE INDEX formazione_lezionecorsobase_7d9c2dba ON formazione_lezionecorsobase USING btree (corso_id);
 8   DROP INDEX public.formazione_lezionecorsobase_7d9c2dba;
       public         postgres    false    266            �           1259    121640 $   formazione_lezionecorsobase_7df656af    INDEX     g   CREATE INDEX formazione_lezionecorsobase_7df656af ON formazione_lezionecorsobase USING btree (inizio);
 8   DROP INDEX public.formazione_lezionecorsobase_7df656af;
       public         postgres    false    266            �           1259    121641 $   formazione_lezionecorsobase_fff25994    INDEX     e   CREATE INDEX formazione_lezionecorsobase_fff25994 ON formazione_lezionecorsobase USING btree (fine);
 8   DROP INDEX public.formazione_lezionecorsobase_fff25994;
       public         postgres    false    266            �           1259    121642 +   formazione_partecipazionecorsobase_057ae320    INDEX     z   CREATE INDEX formazione_partecipazionecorsobase_057ae320 ON formazione_partecipazionecorsobase USING btree (esito_esame);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_057ae320;
       public         postgres    false    268            �           1259    121643 +   formazione_partecipazionecorsobase_36063dc9    INDEX     x   CREATE INDEX formazione_partecipazionecorsobase_36063dc9 ON formazione_partecipazionecorsobase USING btree (creazione);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_36063dc9;
       public         postgres    false    268            �           1259    121644 +   formazione_partecipazionecorsobase_43662d06    INDEX     y   CREATE INDEX formazione_partecipazionecorsobase_43662d06 ON formazione_partecipazionecorsobase USING btree (confermata);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_43662d06;
       public         postgres    false    268            �           1259    121645 +   formazione_partecipazionecorsobase_4a9487af    INDEX     w   CREATE INDEX formazione_partecipazionecorsobase_4a9487af ON formazione_partecipazionecorsobase USING btree (ritirata);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_4a9487af;
       public         postgres    false    268            �           1259    121646 +   formazione_partecipazionecorsobase_69bd2e5f    INDEX     ~   CREATE INDEX formazione_partecipazionecorsobase_69bd2e5f ON formazione_partecipazionecorsobase USING btree (ultima_modifica);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_69bd2e5f;
       public         postgres    false    268            �           1259    121647 +   formazione_partecipazionecorsobase_7d9c2dba    INDEX     w   CREATE INDEX formazione_partecipazionecorsobase_7d9c2dba ON formazione_partecipazionecorsobase USING btree (corso_id);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_7d9c2dba;
       public         postgres    false    268            �           1259    121648 +   formazione_partecipazionecorsobase_95c12757    INDEX     y   CREATE INDEX formazione_partecipazionecorsobase_95c12757 ON formazione_partecipazionecorsobase USING btree (ammissione);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_95c12757;
       public         postgres    false    268            �           1259    121649 +   formazione_partecipazionecorsobase_9ffeed07    INDEX     |   CREATE INDEX formazione_partecipazionecorsobase_9ffeed07 ON formazione_partecipazionecorsobase USING btree (esito_parte_2);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_9ffeed07;
       public         postgres    false    268            �           1259    121650 +   formazione_partecipazionecorsobase_ae23e0a9    INDEX     |   CREATE INDEX formazione_partecipazionecorsobase_ae23e0a9 ON formazione_partecipazionecorsobase USING btree (esito_parte_1);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_ae23e0a9;
       public         postgres    false    268            �           1259    121651 ;   formazione_partecipazionecorsobase_ammissione_c2a4220a_like    INDEX     �   CREATE INDEX formazione_partecipazionecorsobase_ammissione_c2a4220a_like ON formazione_partecipazionecorsobase USING btree (ammissione varchar_pattern_ops);
 O   DROP INDEX public.formazione_partecipazionecorsobase_ammissione_c2a4220a_like;
       public         postgres    false    268            �           1259    121652 +   formazione_partecipazionecorsobase_cb8e6a80    INDEX     ~   CREATE INDEX formazione_partecipazionecorsobase_cb8e6a80 ON formazione_partecipazionecorsobase USING btree (destinazione_id);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_cb8e6a80;
       public         postgres    false    268            �           1259    121653 +   formazione_partecipazionecorsobase_e8589820    INDEX     y   CREATE INDEX formazione_partecipazionecorsobase_e8589820 ON formazione_partecipazionecorsobase USING btree (persona_id);
 ?   DROP INDEX public.formazione_partecipazionecorsobase_e8589820;
       public         postgres    false    268            �           1259    121654 <   formazione_partecipazionecorsobase_esito_esame_d95ad7bd_like    INDEX     �   CREATE INDEX formazione_partecipazionecorsobase_esito_esame_d95ad7bd_like ON formazione_partecipazionecorsobase USING btree (esito_esame varchar_pattern_ops);
 P   DROP INDEX public.formazione_partecipazionecorsobase_esito_esame_d95ad7bd_like;
       public         postgres    false    268            �           1259    121655 >   formazione_partecipazionecorsobase_esito_parte_1_e41db682_like    INDEX     �   CREATE INDEX formazione_partecipazionecorsobase_esito_parte_1_e41db682_like ON formazione_partecipazionecorsobase USING btree (esito_parte_1 varchar_pattern_ops);
 R   DROP INDEX public.formazione_partecipazionecorsobase_esito_parte_1_e41db682_like;
       public         postgres    false    268            �           1259    121656 >   formazione_partecipazionecorsobase_esito_parte_2_1839556d_like    INDEX     �   CREATE INDEX formazione_partecipazionecorsobase_esito_parte_2_1839556d_like ON formazione_partecipazionecorsobase USING btree (esito_parte_2 varchar_pattern_ops);
 R   DROP INDEX public.formazione_partecipazionecorsobase_esito_parte_2_1839556d_like;
       public         postgres    false    268            �           1259    121657    gruppi_appartenenza_179ac911    INDEX     ]   CREATE INDEX gruppi_appartenenza_179ac911 ON gruppi_appartenenza USING btree (negato_da_id);
 0   DROP INDEX public.gruppi_appartenenza_179ac911;
       public         postgres    false    270            �           1259    121658    gruppi_appartenenza_2a93eda0    INDEX     Z   CREATE INDEX gruppi_appartenenza_2a93eda0 ON gruppi_appartenenza USING btree (gruppo_id);
 0   DROP INDEX public.gruppi_appartenenza_2a93eda0;
       public         postgres    false    270            �           1259    121659    gruppi_appartenenza_36063dc9    INDEX     Z   CREATE INDEX gruppi_appartenenza_36063dc9 ON gruppi_appartenenza USING btree (creazione);
 0   DROP INDEX public.gruppi_appartenenza_36063dc9;
       public         postgres    false    270            �           1259    121660    gruppi_appartenenza_69bd2e5f    INDEX     `   CREATE INDEX gruppi_appartenenza_69bd2e5f ON gruppi_appartenenza USING btree (ultima_modifica);
 0   DROP INDEX public.gruppi_appartenenza_69bd2e5f;
       public         postgres    false    270            �           1259    121661    gruppi_appartenenza_7df656af    INDEX     W   CREATE INDEX gruppi_appartenenza_7df656af ON gruppi_appartenenza USING btree (inizio);
 0   DROP INDEX public.gruppi_appartenenza_7df656af;
       public         postgres    false    270            �           1259    121662    gruppi_appartenenza_e8589820    INDEX     [   CREATE INDEX gruppi_appartenenza_e8589820 ON gruppi_appartenenza USING btree (persona_id);
 0   DROP INDEX public.gruppi_appartenenza_e8589820;
       public         postgres    false    270            �           1259    121663    gruppi_appartenenza_fff25994    INDEX     U   CREATE INDEX gruppi_appartenenza_fff25994 ON gruppi_appartenenza USING btree (fine);
 0   DROP INDEX public.gruppi_appartenenza_fff25994;
       public         postgres    false    270            �           1259    121664    gruppi_gruppo_0687f864    INDEX     L   CREATE INDEX gruppi_gruppo_0687f864 ON gruppi_gruppo USING btree (sede_id);
 *   DROP INDEX public.gruppi_gruppo_0687f864;
       public         postgres    false    272            �           1259    121665    gruppi_gruppo_36063dc9    INDEX     N   CREATE INDEX gruppi_gruppo_36063dc9 ON gruppi_gruppo USING btree (creazione);
 *   DROP INDEX public.gruppi_gruppo_36063dc9;
       public         postgres    false    272            �           1259    121666    gruppi_gruppo_3abe1833    INDEX     P   CREATE INDEX gruppi_gruppo_3abe1833 ON gruppi_gruppo USING btree (attivita_id);
 *   DROP INDEX public.gruppi_gruppo_3abe1833;
       public         postgres    false    272            �           1259    121667    gruppi_gruppo_69bd2e5f    INDEX     T   CREATE INDEX gruppi_gruppo_69bd2e5f ON gruppi_gruppo USING btree (ultima_modifica);
 *   DROP INDEX public.gruppi_gruppo_69bd2e5f;
       public         postgres    false    272            �           1259    121668    gruppi_gruppo_cefdb931    INDEX     N   CREATE INDEX gruppi_gruppo_cefdb931 ON gruppi_gruppo USING btree (obiettivo);
 *   DROP INDEX public.gruppi_gruppo_cefdb931;
       public         postgres    false    272            �           1259    121669    gruppi_gruppo_d266de13    INDEX     L   CREATE INDEX gruppi_gruppo_d266de13 ON gruppi_gruppo USING btree (area_id);
 *   DROP INDEX public.gruppi_gruppo_d266de13;
       public         postgres    false    272            �           1259    121670    gruppi_gruppo_dbb9a234    INDEX     O   CREATE INDEX gruppi_gruppo_dbb9a234 ON gruppi_gruppo USING btree (estensione);
 *   DROP INDEX public.gruppi_gruppo_dbb9a234;
       public         postgres    false    272            �           1259    121671 &   gruppi_gruppo_estensione_0c1e2168_like    INDEX     s   CREATE INDEX gruppi_gruppo_estensione_0c1e2168_like ON gruppi_gruppo USING btree (estensione varchar_pattern_ops);
 :   DROP INDEX public.gruppi_gruppo_estensione_0c1e2168_like;
       public         postgres    false    272            �           1259    121672    patenti_elemento_36063dc9    INDEX     T   CREATE INDEX patenti_elemento_36063dc9 ON patenti_elemento USING btree (creazione);
 -   DROP INDEX public.patenti_elemento_36063dc9;
       public         postgres    false    274            �           1259    121673    patenti_elemento_43662d06    INDEX     U   CREATE INDEX patenti_elemento_43662d06 ON patenti_elemento USING btree (confermata);
 -   DROP INDEX public.patenti_elemento_43662d06;
       public         postgres    false    274            �           1259    121674    patenti_elemento_4a9487af    INDEX     S   CREATE INDEX patenti_elemento_4a9487af ON patenti_elemento USING btree (ritirata);
 -   DROP INDEX public.patenti_elemento_4a9487af;
       public         postgres    false    274            �           1259    121675    patenti_elemento_69bd2e5f    INDEX     Z   CREATE INDEX patenti_elemento_69bd2e5f ON patenti_elemento USING btree (ultima_modifica);
 -   DROP INDEX public.patenti_elemento_69bd2e5f;
       public         postgres    false    274            �           1259    121676    patenti_patente_36063dc9    INDEX     R   CREATE INDEX patenti_patente_36063dc9 ON patenti_patente USING btree (creazione);
 ,   DROP INDEX public.patenti_patente_36063dc9;
       public         postgres    false    276            �           1259    121677    patenti_patente_69bd2e5f    INDEX     X   CREATE INDEX patenti_patente_69bd2e5f ON patenti_patente USING btree (ultima_modifica);
 ,   DROP INDEX public.patenti_patente_69bd2e5f;
       public         postgres    false    276            �           1259    121678    posta_destinatario_36063dc9    INDEX     X   CREATE INDEX posta_destinatario_36063dc9 ON posta_destinatario USING btree (creazione);
 /   DROP INDEX public.posta_destinatario_36063dc9;
       public         postgres    false    278            �           1259    121679    posta_destinatario_69bd2e5f    INDEX     ^   CREATE INDEX posta_destinatario_69bd2e5f ON posta_destinatario USING btree (ultima_modifica);
 /   DROP INDEX public.posta_destinatario_69bd2e5f;
       public         postgres    false    278            �           1259    121680    posta_destinatario_e8589820    INDEX     Y   CREATE INDEX posta_destinatario_e8589820 ON posta_destinatario USING btree (persona_id);
 /   DROP INDEX public.posta_destinatario_e8589820;
       public         postgres    false    278            �           1259    121681 '   posta_destinatario_errore_676732c7_like    INDEX     u   CREATE INDEX posta_destinatario_errore_676732c7_like ON posta_destinatario USING btree (errore varchar_pattern_ops);
 ;   DROP INDEX public.posta_destinatario_errore_676732c7_like;
       public         postgres    false    278            �           1259    121682 '   posta_destinatario_errore_676732c7_uniq    INDEX     a   CREATE INDEX posta_destinatario_errore_676732c7_uniq ON posta_destinatario USING btree (errore);
 ;   DROP INDEX public.posta_destinatario_errore_676732c7_uniq;
       public         postgres    false    278            �           1259    121683    posta_destinatario_f7a5b550    INDEX     [   CREATE INDEX posta_destinatario_f7a5b550 ON posta_destinatario USING btree (messaggio_id);
 /   DROP INDEX public.posta_destinatario_f7a5b550;
       public         postgres    false    278                        1259    121684 (   posta_destinatario_inviato_b20d2d83_uniq    INDEX     c   CREATE INDEX posta_destinatario_inviato_b20d2d83_uniq ON posta_destinatario USING btree (inviato);
 <   DROP INDEX public.posta_destinatario_inviato_b20d2d83_uniq;
       public         postgres    false    278                       1259    121685 *   posta_destinatario_tentativo_4685f3b8_uniq    INDEX     g   CREATE INDEX posta_destinatario_tentativo_4685f3b8_uniq ON posta_destinatario USING btree (tentativo);
 >   DROP INDEX public.posta_destinatario_tentativo_4685f3b8_uniq;
       public         postgres    false    278                       1259    121686    posta_messaggio_36063dc9    INDEX     R   CREATE INDEX posta_messaggio_36063dc9 ON posta_messaggio USING btree (creazione);
 ,   DROP INDEX public.posta_messaggio_36063dc9;
       public         postgres    false    280                       1259    121687    posta_messaggio_4ca5d3ec    INDEX     P   CREATE INDEX posta_messaggio_4ca5d3ec ON posta_messaggio USING btree (oggetto);
 ,   DROP INDEX public.posta_messaggio_4ca5d3ec;
       public         postgres    false    280                       1259    121688    posta_messaggio_69bd2e5f    INDEX     X   CREATE INDEX posta_messaggio_69bd2e5f ON posta_messaggio USING btree (ultima_modifica);
 ,   DROP INDEX public.posta_messaggio_69bd2e5f;
       public         postgres    false    280                       1259    121689    posta_messaggio_a8472066    INDEX     T   CREATE INDEX posta_messaggio_a8472066 ON posta_messaggio USING btree (mittente_id);
 ,   DROP INDEX public.posta_messaggio_a8472066;
       public         postgres    false    280                       1259    121690    posta_messaggio_db29de29    INDEX     V   CREATE INDEX posta_messaggio_db29de29 ON posta_messaggio USING btree (rispondi_a_id);
 ,   DROP INDEX public.posta_messaggio_db29de29;
       public         postgres    false    280            	           1259    121691 %   posta_messaggio_oggetto_a0c88b4e_like    INDEX     q   CREATE INDEX posta_messaggio_oggetto_a0c88b4e_like ON posta_messaggio USING btree (oggetto varchar_pattern_ops);
 9   DROP INDEX public.posta_messaggio_oggetto_a0c88b4e_like;
       public         postgres    false    280                       1259    121692    sangue_donatore_2ca2c264    INDEX     S   CREATE INDEX sangue_donatore_2ca2c264 ON sangue_donatore USING btree (fattore_rh);
 ,   DROP INDEX public.sangue_donatore_2ca2c264;
       public         postgres    false    282                       1259    121693    sangue_donatore_36063dc9    INDEX     R   CREATE INDEX sangue_donatore_36063dc9 ON sangue_donatore USING btree (creazione);
 ,   DROP INDEX public.sangue_donatore_36063dc9;
       public         postgres    false    282                       1259    121694    sangue_donatore_458a48a0    INDEX     T   CREATE INDEX sangue_donatore_458a48a0 ON sangue_donatore USING btree (fanotipo_rh);
 ,   DROP INDEX public.sangue_donatore_458a48a0;
       public         postgres    false    282                       1259    121695    sangue_donatore_69bd2e5f    INDEX     X   CREATE INDEX sangue_donatore_69bd2e5f ON sangue_donatore USING btree (ultima_modifica);
 ,   DROP INDEX public.sangue_donatore_69bd2e5f;
       public         postgres    false    282                       1259    121696    sangue_donatore_8ab2456d    INDEX     T   CREATE INDEX sangue_donatore_8ab2456d ON sangue_donatore USING btree (sede_sit_id);
 ,   DROP INDEX public.sangue_donatore_8ab2456d;
       public         postgres    false    282                       1259    121697    sangue_donatore_921254a0    INDEX     S   CREATE INDEX sangue_donatore_921254a0 ON sangue_donatore USING btree (codice_sit);
 ,   DROP INDEX public.sangue_donatore_921254a0;
       public         postgres    false    282                       1259    121698 (   sangue_donatore_codice_sit_44e79323_like    INDEX     w   CREATE INDEX sangue_donatore_codice_sit_44e79323_like ON sangue_donatore USING btree (codice_sit varchar_pattern_ops);
 <   DROP INDEX public.sangue_donatore_codice_sit_44e79323_like;
       public         postgres    false    282                       1259    121699    sangue_donatore_d456622a    INDEX     Y   CREATE INDEX sangue_donatore_d456622a ON sangue_donatore USING btree (gruppo_sanguigno);
 ,   DROP INDEX public.sangue_donatore_d456622a;
       public         postgres    false    282                       1259    121700 )   sangue_donatore_fanotipo_rh_ce13bb26_like    INDEX     y   CREATE INDEX sangue_donatore_fanotipo_rh_ce13bb26_like ON sangue_donatore USING btree (fanotipo_rh varchar_pattern_ops);
 =   DROP INDEX public.sangue_donatore_fanotipo_rh_ce13bb26_like;
       public         postgres    false    282                       1259    121701 (   sangue_donatore_fattore_rh_e988c055_like    INDEX     w   CREATE INDEX sangue_donatore_fattore_rh_e988c055_like ON sangue_donatore USING btree (fattore_rh varchar_pattern_ops);
 <   DROP INDEX public.sangue_donatore_fattore_rh_e988c055_like;
       public         postgres    false    282                       1259    121702 .   sangue_donatore_gruppo_sanguigno_493a48ff_like    INDEX     �   CREATE INDEX sangue_donatore_gruppo_sanguigno_493a48ff_like ON sangue_donatore USING btree (gruppo_sanguigno varchar_pattern_ops);
 B   DROP INDEX public.sangue_donatore_gruppo_sanguigno_493a48ff_like;
       public         postgres    false    282                       1259    121703    sangue_donazione_0687f864    INDEX     R   CREATE INDEX sangue_donazione_0687f864 ON sangue_donazione USING btree (sede_id);
 -   DROP INDEX public.sangue_donazione_0687f864;
       public         postgres    false    284                       1259    121704    sangue_donazione_36063dc9    INDEX     T   CREATE INDEX sangue_donazione_36063dc9 ON sangue_donazione USING btree (creazione);
 -   DROP INDEX public.sangue_donazione_36063dc9;
       public         postgres    false    284                       1259    121705    sangue_donazione_401281b0    INDEX     O   CREATE INDEX sangue_donazione_401281b0 ON sangue_donazione USING btree (tipo);
 -   DROP INDEX public.sangue_donazione_401281b0;
       public         postgres    false    284                       1259    121706    sangue_donazione_43662d06    INDEX     U   CREATE INDEX sangue_donazione_43662d06 ON sangue_donazione USING btree (confermata);
 -   DROP INDEX public.sangue_donazione_43662d06;
       public         postgres    false    284                       1259    121707    sangue_donazione_4a9487af    INDEX     S   CREATE INDEX sangue_donazione_4a9487af ON sangue_donazione USING btree (ritirata);
 -   DROP INDEX public.sangue_donazione_4a9487af;
       public         postgres    false    284                        1259    121708    sangue_donazione_69bd2e5f    INDEX     Z   CREATE INDEX sangue_donazione_69bd2e5f ON sangue_donazione USING btree (ultima_modifica);
 -   DROP INDEX public.sangue_donazione_69bd2e5f;
       public         postgres    false    284            !           1259    121709    sangue_donazione_e8589820    INDEX     U   CREATE INDEX sangue_donazione_e8589820 ON sangue_donazione USING btree (persona_id);
 -   DROP INDEX public.sangue_donazione_e8589820;
       public         postgres    false    284            $           1259    121710 #   sangue_donazione_tipo_4067a24a_like    INDEX     m   CREATE INDEX sangue_donazione_tipo_4067a24a_like ON sangue_donazione USING btree (tipo varchar_pattern_ops);
 7   DROP INDEX public.sangue_donazione_tipo_4067a24a_like;
       public         postgres    false    284            %           1259    121711    sangue_merito_36063dc9    INDEX     N   CREATE INDEX sangue_merito_36063dc9 ON sangue_merito USING btree (creazione);
 *   DROP INDEX public.sangue_merito_36063dc9;
       public         postgres    false    286            &           1259    121712    sangue_merito_69bd2e5f    INDEX     T   CREATE INDEX sangue_merito_69bd2e5f ON sangue_merito USING btree (ultima_modifica);
 *   DROP INDEX public.sangue_merito_69bd2e5f;
       public         postgres    false    286            '           1259    121713    sangue_merito_bd4ddd0a    INDEX     N   CREATE INDEX sangue_merito_bd4ddd0a ON sangue_merito USING btree (donazione);
 *   DROP INDEX public.sangue_merito_bd4ddd0a;
       public         postgres    false    286            (           1259    121714 %   sangue_merito_donazione_7fbd7550_like    INDEX     q   CREATE INDEX sangue_merito_donazione_7fbd7550_like ON sangue_merito USING btree (donazione varchar_pattern_ops);
 9   DROP INDEX public.sangue_merito_donazione_7fbd7550_like;
       public         postgres    false    286            )           1259    121715    sangue_merito_e8589820    INDEX     O   CREATE INDEX sangue_merito_e8589820 ON sangue_merito USING btree (persona_id);
 *   DROP INDEX public.sangue_merito_e8589820;
       public         postgres    false    286            .           1259    121716    social_commento_36063dc9    INDEX     R   CREATE INDEX social_commento_36063dc9 ON social_commento USING btree (creazione);
 ,   DROP INDEX public.social_commento_36063dc9;
       public         postgres    false    290            /           1259    121717    social_commento_69bd2e5f    INDEX     X   CREATE INDEX social_commento_69bd2e5f ON social_commento USING btree (ultima_modifica);
 ,   DROP INDEX public.social_commento_69bd2e5f;
       public         postgres    false    290            0           1259    121718    social_commento_9c82ce86    INDEX     S   CREATE INDEX social_commento_9c82ce86 ON social_commento USING btree (oggetto_id);
 ,   DROP INDEX public.social_commento_9c82ce86;
       public         postgres    false    290            1           1259    121719    social_commento_fa6f1f24    INDEX     R   CREATE INDEX social_commento_fa6f1f24 ON social_commento USING btree (autore_id);
 ,   DROP INDEX public.social_commento_fa6f1f24;
       public         postgres    false    290            2           1259    121720    social_commento_fe2a0979    INDEX     X   CREATE INDEX social_commento_fe2a0979 ON social_commento USING btree (oggetto_tipo_id);
 ,   DROP INDEX public.social_commento_fe2a0979;
       public         postgres    false    290            5           1259    121721    social_giudizio_20e6d3fc    INDEX     Q   CREATE INDEX social_giudizio_20e6d3fc ON social_giudizio USING btree (positivo);
 ,   DROP INDEX public.social_giudizio_20e6d3fc;
       public         postgres    false    292            6           1259    121722    social_giudizio_36063dc9    INDEX     R   CREATE INDEX social_giudizio_36063dc9 ON social_giudizio USING btree (creazione);
 ,   DROP INDEX public.social_giudizio_36063dc9;
       public         postgres    false    292            7           1259    121723    social_giudizio_69bd2e5f    INDEX     X   CREATE INDEX social_giudizio_69bd2e5f ON social_giudizio USING btree (ultima_modifica);
 ,   DROP INDEX public.social_giudizio_69bd2e5f;
       public         postgres    false    292            8           1259    121724    social_giudizio_9c82ce86    INDEX     S   CREATE INDEX social_giudizio_9c82ce86 ON social_giudizio USING btree (oggetto_id);
 ,   DROP INDEX public.social_giudizio_9c82ce86;
       public         postgres    false    292            9           1259    121725    social_giudizio_fa6f1f24    INDEX     R   CREATE INDEX social_giudizio_fa6f1f24 ON social_giudizio USING btree (autore_id);
 ,   DROP INDEX public.social_giudizio_fa6f1f24;
       public         postgres    false    292            :           1259    121726    social_giudizio_fe2a0979    INDEX     X   CREATE INDEX social_giudizio_fe2a0979 ON social_giudizio USING btree (oggetto_tipo_id);
 ,   DROP INDEX public.social_giudizio_fe2a0979;
       public         postgres    false    292            =           1259    121727 #   thumbnail_kvstore_key_3f850178_like    INDEX     m   CREATE INDEX thumbnail_kvstore_key_3f850178_like ON thumbnail_kvstore USING btree (key varchar_pattern_ops);
 7   DROP INDEX public.thumbnail_kvstore_key_3f850178_like;
       public         postgres    false    294            @           1259    121728    ufficio_soci_quota_0687f864    INDEX     V   CREATE INDEX ufficio_soci_quota_0687f864 ON ufficio_soci_quota USING btree (sede_id);
 /   DROP INDEX public.ufficio_soci_quota_0687f864;
       public         postgres    false    295            A           1259    121729    ufficio_soci_quota_36063dc9    INDEX     X   CREATE INDEX ufficio_soci_quota_36063dc9 ON ufficio_soci_quota USING btree (creazione);
 /   DROP INDEX public.ufficio_soci_quota_36063dc9;
       public         postgres    false    295            B           1259    121730    ufficio_soci_quota_530b0ac8    INDEX     ^   CREATE INDEX ufficio_soci_quota_530b0ac8 ON ufficio_soci_quota USING btree (appartenenza_id);
 /   DROP INDEX public.ufficio_soci_quota_530b0ac8;
       public         postgres    false    295            C           1259    121731    ufficio_soci_quota_5744ea4d    INDEX     _   CREATE INDEX ufficio_soci_quota_5744ea4d ON ufficio_soci_quota USING btree (registrato_da_id);
 /   DROP INDEX public.ufficio_soci_quota_5744ea4d;
       public         postgres    false    295            D           1259    121732    ufficio_soci_quota_69bd2e5f    INDEX     ^   CREATE INDEX ufficio_soci_quota_69bd2e5f ON ufficio_soci_quota USING btree (ultima_modifica);
 /   DROP INDEX public.ufficio_soci_quota_69bd2e5f;
       public         postgres    false    295            E           1259    121733    ufficio_soci_quota_6b81ba8e    INDEX     Z   CREATE INDEX ufficio_soci_quota_6b81ba8e ON ufficio_soci_quota USING btree (progressivo);
 /   DROP INDEX public.ufficio_soci_quota_6b81ba8e;
       public         postgres    false    295            F           1259    121734    ufficio_soci_quota_7b84f719    INDEX     ^   CREATE INDEX ufficio_soci_quota_7b84f719 ON ufficio_soci_quota USING btree (annullato_da_id);
 /   DROP INDEX public.ufficio_soci_quota_7b84f719;
       public         postgres    false    295            G           1259    121735    ufficio_soci_quota_d6ef5c1f    INDEX     Y   CREATE INDEX ufficio_soci_quota_d6ef5c1f ON ufficio_soci_quota USING btree (vecchio_id);
 /   DROP INDEX public.ufficio_soci_quota_d6ef5c1f;
       public         postgres    false    295            H           1259    121736    ufficio_soci_quota_ddc70b20    INDEX     S   CREATE INDEX ufficio_soci_quota_ddc70b20 ON ufficio_soci_quota USING btree (anno);
 /   DROP INDEX public.ufficio_soci_quota_ddc70b20;
       public         postgres    false    295            I           1259    121737    ufficio_soci_quota_e0b406f5    INDEX     T   CREATE INDEX ufficio_soci_quota_e0b406f5 ON ufficio_soci_quota USING btree (stato);
 /   DROP INDEX public.ufficio_soci_quota_e0b406f5;
       public         postgres    false    295            J           1259    121738    ufficio_soci_quota_e8589820    INDEX     Y   CREATE INDEX ufficio_soci_quota_e8589820 ON ufficio_soci_quota USING btree (persona_id);
 /   DROP INDEX public.ufficio_soci_quota_e8589820;
       public         postgres    false    295            O           1259    121739 &   ufficio_soci_quota_stato_d1d379cb_like    INDEX     s   CREATE INDEX ufficio_soci_quota_stato_d1d379cb_like ON ufficio_soci_quota USING btree (stato varchar_pattern_ops);
 :   DROP INDEX public.ufficio_soci_quota_stato_d1d379cb_like;
       public         postgres    false    295            P           1259    121740 "   ufficio_soci_tesseramento_36063dc9    INDEX     f   CREATE INDEX ufficio_soci_tesseramento_36063dc9 ON ufficio_soci_tesseramento USING btree (creazione);
 6   DROP INDEX public.ufficio_soci_tesseramento_36063dc9;
       public         postgres    false    297            Q           1259    121741 "   ufficio_soci_tesseramento_69bd2e5f    INDEX     l   CREATE INDEX ufficio_soci_tesseramento_69bd2e5f ON ufficio_soci_tesseramento USING btree (ultima_modifica);
 6   DROP INDEX public.ufficio_soci_tesseramento_69bd2e5f;
       public         postgres    false    297            R           1259    121742 "   ufficio_soci_tesseramento_7df656af    INDEX     c   CREATE INDEX ufficio_soci_tesseramento_7df656af ON ufficio_soci_tesseramento USING btree (inizio);
 6   DROP INDEX public.ufficio_soci_tesseramento_7df656af;
       public         postgres    false    297            W           1259    121743    ufficio_soci_tesserino_029da785    INDEX     g   CREATE INDEX ufficio_soci_tesserino_029da785 ON ufficio_soci_tesserino USING btree (confermato_da_id);
 3   DROP INDEX public.ufficio_soci_tesserino_029da785;
       public         postgres    false    299            X           1259    121744    ufficio_soci_tesserino_1b671890    INDEX     f   CREATE INDEX ufficio_soci_tesserino_1b671890 ON ufficio_soci_tesserino USING btree (data_riconsegna);
 3   DROP INDEX public.ufficio_soci_tesserino_1b671890;
       public         postgres    false    299            Y           1259    121745    ufficio_soci_tesserino_36063dc9    INDEX     `   CREATE INDEX ufficio_soci_tesserino_36063dc9 ON ufficio_soci_tesserino USING btree (creazione);
 3   DROP INDEX public.ufficio_soci_tesserino_36063dc9;
       public         postgres    false    299            Z           1259    121746    ufficio_soci_tesserino_39d25c20    INDEX     ]   CREATE INDEX ufficio_soci_tesserino_39d25c20 ON ufficio_soci_tesserino USING btree (valido);
 3   DROP INDEX public.ufficio_soci_tesserino_39d25c20;
       public         postgres    false    299            [           1259    121747    ufficio_soci_tesserino_41fbc503    INDEX     e   CREATE INDEX ufficio_soci_tesserino_41fbc503 ON ufficio_soci_tesserino USING btree (tipo_richiesta);
 3   DROP INDEX public.ufficio_soci_tesserino_41fbc503;
       public         postgres    false    299            \           1259    121748    ufficio_soci_tesserino_630672f9    INDEX     d   CREATE INDEX ufficio_soci_tesserino_630672f9 ON ufficio_soci_tesserino USING btree (data_conferma);
 3   DROP INDEX public.ufficio_soci_tesserino_630672f9;
       public         postgres    false    299            ]           1259    121749    ufficio_soci_tesserino_69bd2e5f    INDEX     f   CREATE INDEX ufficio_soci_tesserino_69bd2e5f ON ufficio_soci_tesserino USING btree (ultima_modifica);
 3   DROP INDEX public.ufficio_soci_tesserino_69bd2e5f;
       public         postgres    false    299            ^           1259    121750    ufficio_soci_tesserino_7b64dbf8    INDEX     f   CREATE INDEX ufficio_soci_tesserino_7b64dbf8 ON ufficio_soci_tesserino USING btree (richiesto_da_id);
 3   DROP INDEX public.ufficio_soci_tesserino_7b64dbf8;
       public         postgres    false    299            _           1259    121751    ufficio_soci_tesserino_89d87e51    INDEX     f   CREATE INDEX ufficio_soci_tesserino_89d87e51 ON ufficio_soci_tesserino USING btree (stato_richiesta);
 3   DROP INDEX public.ufficio_soci_tesserino_89d87e51;
       public         postgres    false    299            `           1259    121752    ufficio_soci_tesserino_9aa329e5    INDEX     c   CREATE INDEX ufficio_soci_tesserino_9aa329e5 ON ufficio_soci_tesserino USING btree (emesso_da_id);
 3   DROP INDEX public.ufficio_soci_tesserino_9aa329e5;
       public         postgres    false    299            a           1259    121753    ufficio_soci_tesserino_b8ae2251    INDEX     h   CREATE INDEX ufficio_soci_tesserino_b8ae2251 ON ufficio_soci_tesserino USING btree (riconsegnato_a_id);
 3   DROP INDEX public.ufficio_soci_tesserino_b8ae2251;
       public         postgres    false    299            b           1259    121754 +   ufficio_soci_tesserino_codice_2c7aee6f_like    INDEX     }   CREATE INDEX ufficio_soci_tesserino_codice_2c7aee6f_like ON ufficio_soci_tesserino USING btree (codice varchar_pattern_ops);
 ?   DROP INDEX public.ufficio_soci_tesserino_codice_2c7aee6f_like;
       public         postgres    false    299            e           1259    121755    ufficio_soci_tesserino_e8589820    INDEX     a   CREATE INDEX ufficio_soci_tesserino_e8589820 ON ufficio_soci_tesserino USING btree (persona_id);
 3   DROP INDEX public.ufficio_soci_tesserino_e8589820;
       public         postgres    false    299            h           1259    121756 4   ufficio_soci_tesserino_stato_richiesta_d92e7f2f_like    INDEX     �   CREATE INDEX ufficio_soci_tesserino_stato_richiesta_d92e7f2f_like ON ufficio_soci_tesserino USING btree (stato_richiesta varchar_pattern_ops);
 H   DROP INDEX public.ufficio_soci_tesserino_stato_richiesta_d92e7f2f_like;
       public         postgres    false    299            i           1259    121757 3   ufficio_soci_tesserino_tipo_richiesta_2f5d7706_like    INDEX     �   CREATE INDEX ufficio_soci_tesserino_tipo_richiesta_2f5d7706_like ON ufficio_soci_tesserino USING btree (tipo_richiesta varchar_pattern_ops);
 G   DROP INDEX public.ufficio_soci_tesserino_tipo_richiesta_2f5d7706_like;
       public         postgres    false    299            j           1259    121758    veicoli_autoparco_0687f864    INDEX     T   CREATE INDEX veicoli_autoparco_0687f864 ON veicoli_autoparco USING btree (sede_id);
 .   DROP INDEX public.veicoli_autoparco_0687f864;
       public         postgres    false    301            k           1259    121759    veicoli_autoparco_29a104e3    INDEX     Y   CREATE INDEX veicoli_autoparco_29a104e3 ON veicoli_autoparco USING btree (locazione_id);
 .   DROP INDEX public.veicoli_autoparco_29a104e3;
       public         postgres    false    301            l           1259    121760    veicoli_autoparco_36063dc9    INDEX     V   CREATE INDEX veicoli_autoparco_36063dc9 ON veicoli_autoparco USING btree (creazione);
 .   DROP INDEX public.veicoli_autoparco_36063dc9;
       public         postgres    false    301            m           1259    121761    veicoli_autoparco_69bd2e5f    INDEX     \   CREATE INDEX veicoli_autoparco_69bd2e5f ON veicoli_autoparco USING btree (ultima_modifica);
 .   DROP INDEX public.veicoli_autoparco_69bd2e5f;
       public         postgres    false    301            n           1259    121762    veicoli_autoparco_dbb9a234    INDEX     W   CREATE INDEX veicoli_autoparco_dbb9a234 ON veicoli_autoparco USING btree (estensione);
 .   DROP INDEX public.veicoli_autoparco_dbb9a234;
       public         postgres    false    301            o           1259    121763 *   veicoli_autoparco_estensione_202ee0fc_like    INDEX     {   CREATE INDEX veicoli_autoparco_estensione_202ee0fc_like ON veicoli_autoparco USING btree (estensione varchar_pattern_ops);
 >   DROP INDEX public.veicoli_autoparco_estensione_202ee0fc_like;
       public         postgres    false    301            p           1259    121764 $   veicoli_autoparco_nome_067f35a6_like    INDEX     o   CREATE INDEX veicoli_autoparco_nome_067f35a6_like ON veicoli_autoparco USING btree (nome varchar_pattern_ops);
 8   DROP INDEX public.veicoli_autoparco_nome_067f35a6_like;
       public         postgres    false    301            q           1259    121765 $   veicoli_autoparco_nome_067f35a6_uniq    INDEX     [   CREATE INDEX veicoli_autoparco_nome_067f35a6_uniq ON veicoli_autoparco USING btree (nome);
 8   DROP INDEX public.veicoli_autoparco_nome_067f35a6_uniq;
       public         postgres    false    301            t           1259    121766    veicoli_collocazione_2371601c    INDEX     _   CREATE INDEX veicoli_collocazione_2371601c ON veicoli_collocazione USING btree (autoparco_id);
 1   DROP INDEX public.veicoli_collocazione_2371601c;
       public         postgres    false    303            u           1259    121767    veicoli_collocazione_36063dc9    INDEX     \   CREATE INDEX veicoli_collocazione_36063dc9 ON veicoli_collocazione USING btree (creazione);
 1   DROP INDEX public.veicoli_collocazione_36063dc9;
       public         postgres    false    303            v           1259    121768    veicoli_collocazione_69bd2e5f    INDEX     b   CREATE INDEX veicoli_collocazione_69bd2e5f ON veicoli_collocazione USING btree (ultima_modifica);
 1   DROP INDEX public.veicoli_collocazione_69bd2e5f;
       public         postgres    false    303            w           1259    121769    veicoli_collocazione_7df656af    INDEX     Y   CREATE INDEX veicoli_collocazione_7df656af ON veicoli_collocazione USING btree (inizio);
 1   DROP INDEX public.veicoli_collocazione_7df656af;
       public         postgres    false    303            x           1259    121770    veicoli_collocazione_910c7f61    INDEX     _   CREATE INDEX veicoli_collocazione_910c7f61 ON veicoli_collocazione USING btree (creato_da_id);
 1   DROP INDEX public.veicoli_collocazione_910c7f61;
       public         postgres    false    303            y           1259    121771    veicoli_collocazione_9431c155    INDEX     ]   CREATE INDEX veicoli_collocazione_9431c155 ON veicoli_collocazione USING btree (veicolo_id);
 1   DROP INDEX public.veicoli_collocazione_9431c155;
       public         postgres    false    303            z           1259    121772    veicoli_collocazione_fff25994    INDEX     W   CREATE INDEX veicoli_collocazione_fff25994 ON veicoli_collocazione USING btree (fine);
 1   DROP INDEX public.veicoli_collocazione_fff25994;
       public         postgres    false    303            }           1259    121773    veicoli_fermotecnico_36063dc9    INDEX     \   CREATE INDEX veicoli_fermotecnico_36063dc9 ON veicoli_fermotecnico USING btree (creazione);
 1   DROP INDEX public.veicoli_fermotecnico_36063dc9;
       public         postgres    false    305            ~           1259    121774    veicoli_fermotecnico_69bd2e5f    INDEX     b   CREATE INDEX veicoli_fermotecnico_69bd2e5f ON veicoli_fermotecnico USING btree (ultima_modifica);
 1   DROP INDEX public.veicoli_fermotecnico_69bd2e5f;
       public         postgres    false    305                       1259    121775    veicoli_fermotecnico_7df656af    INDEX     Y   CREATE INDEX veicoli_fermotecnico_7df656af ON veicoli_fermotecnico USING btree (inizio);
 1   DROP INDEX public.veicoli_fermotecnico_7df656af;
       public         postgres    false    305            �           1259    121776    veicoli_fermotecnico_910c7f61    INDEX     _   CREATE INDEX veicoli_fermotecnico_910c7f61 ON veicoli_fermotecnico USING btree (creato_da_id);
 1   DROP INDEX public.veicoli_fermotecnico_910c7f61;
       public         postgres    false    305            �           1259    121777    veicoli_fermotecnico_9431c155    INDEX     ]   CREATE INDEX veicoli_fermotecnico_9431c155 ON veicoli_fermotecnico USING btree (veicolo_id);
 1   DROP INDEX public.veicoli_fermotecnico_9431c155;
       public         postgres    false    305            �           1259    121778    veicoli_fermotecnico_fff25994    INDEX     W   CREATE INDEX veicoli_fermotecnico_fff25994 ON veicoli_fermotecnico USING btree (fine);
 1   DROP INDEX public.veicoli_fermotecnico_fff25994;
       public         postgres    false    305            �           1259    121779    veicoli_manutenzione_36063dc9    INDEX     \   CREATE INDEX veicoli_manutenzione_36063dc9 ON veicoli_manutenzione USING btree (creazione);
 1   DROP INDEX public.veicoli_manutenzione_36063dc9;
       public         postgres    false    307            �           1259    121780    veicoli_manutenzione_401281b0    INDEX     W   CREATE INDEX veicoli_manutenzione_401281b0 ON veicoli_manutenzione USING btree (tipo);
 1   DROP INDEX public.veicoli_manutenzione_401281b0;
       public         postgres    false    307            �           1259    121781    veicoli_manutenzione_69bd2e5f    INDEX     b   CREATE INDEX veicoli_manutenzione_69bd2e5f ON veicoli_manutenzione USING btree (ultima_modifica);
 1   DROP INDEX public.veicoli_manutenzione_69bd2e5f;
       public         postgres    false    307            �           1259    121782    veicoli_manutenzione_8d777f38    INDEX     W   CREATE INDEX veicoli_manutenzione_8d777f38 ON veicoli_manutenzione USING btree (data);
 1   DROP INDEX public.veicoli_manutenzione_8d777f38;
       public         postgres    false    307            �           1259    121783    veicoli_manutenzione_910c7f61    INDEX     _   CREATE INDEX veicoli_manutenzione_910c7f61 ON veicoli_manutenzione USING btree (creato_da_id);
 1   DROP INDEX public.veicoli_manutenzione_910c7f61;
       public         postgres    false    307            �           1259    121784    veicoli_manutenzione_9431c155    INDEX     ]   CREATE INDEX veicoli_manutenzione_9431c155 ON veicoli_manutenzione USING btree (veicolo_id);
 1   DROP INDEX public.veicoli_manutenzione_9431c155;
       public         postgres    false    307            �           1259    121785 '   veicoli_manutenzione_tipo_8709d1fd_like    INDEX     u   CREATE INDEX veicoli_manutenzione_tipo_8709d1fd_like ON veicoli_manutenzione USING btree (tipo varchar_pattern_ops);
 ;   DROP INDEX public.veicoli_manutenzione_tipo_8709d1fd_like;
       public         postgres    false    307            �           1259    121786    veicoli_rifornimento_201b1ff3    INDEX     [   CREATE INDEX veicoli_rifornimento_201b1ff3 ON veicoli_rifornimento USING btree (ricevuta);
 1   DROP INDEX public.veicoli_rifornimento_201b1ff3;
       public         postgres    false    309            �           1259    121787    veicoli_rifornimento_311a4e62    INDEX     b   CREATE INDEX veicoli_rifornimento_311a4e62 ON veicoli_rifornimento USING btree (contachilometri);
 1   DROP INDEX public.veicoli_rifornimento_311a4e62;
       public         postgres    false    309            �           1259    121788    veicoli_rifornimento_36063dc9    INDEX     \   CREATE INDEX veicoli_rifornimento_36063dc9 ON veicoli_rifornimento USING btree (creazione);
 1   DROP INDEX public.veicoli_rifornimento_36063dc9;
       public         postgres    false    309            �           1259    121789    veicoli_rifornimento_69bd2e5f    INDEX     b   CREATE INDEX veicoli_rifornimento_69bd2e5f ON veicoli_rifornimento USING btree (ultima_modifica);
 1   DROP INDEX public.veicoli_rifornimento_69bd2e5f;
       public         postgres    false    309            �           1259    121790    veicoli_rifornimento_8d777f38    INDEX     W   CREATE INDEX veicoli_rifornimento_8d777f38 ON veicoli_rifornimento USING btree (data);
 1   DROP INDEX public.veicoli_rifornimento_8d777f38;
       public         postgres    false    309            �           1259    121791    veicoli_rifornimento_910c7f61    INDEX     _   CREATE INDEX veicoli_rifornimento_910c7f61 ON veicoli_rifornimento USING btree (creato_da_id);
 1   DROP INDEX public.veicoli_rifornimento_910c7f61;
       public         postgres    false    309            �           1259    121792    veicoli_rifornimento_9431c155    INDEX     ]   CREATE INDEX veicoli_rifornimento_9431c155 ON veicoli_rifornimento USING btree (veicolo_id);
 1   DROP INDEX public.veicoli_rifornimento_9431c155;
       public         postgres    false    309            �           1259    121793    veicoli_rifornimento_a60e15d9    INDEX     X   CREATE INDEX veicoli_rifornimento_a60e15d9 ON veicoli_rifornimento USING btree (costo);
 1   DROP INDEX public.veicoli_rifornimento_a60e15d9;
       public         postgres    false    309            �           1259    121794    veicoli_rifornimento_ad33195f    INDEX     ]   CREATE INDEX veicoli_rifornimento_ad33195f ON veicoli_rifornimento USING btree (contalitri);
 1   DROP INDEX public.veicoli_rifornimento_ad33195f;
       public         postgres    false    309            �           1259    121795    veicoli_rifornimento_da1f0ca4    INDEX     e   CREATE INDEX veicoli_rifornimento_da1f0ca4 ON veicoli_rifornimento USING btree (consumo_carburante);
 1   DROP INDEX public.veicoli_rifornimento_da1f0ca4;
       public         postgres    false    309            �           1259    121796 +   veicoli_rifornimento_ricevuta_bd9a2b26_like    INDEX     }   CREATE INDEX veicoli_rifornimento_ricevuta_bd9a2b26_like ON veicoli_rifornimento USING btree (ricevuta varchar_pattern_ops);
 ?   DROP INDEX public.veicoli_rifornimento_ricevuta_bd9a2b26_like;
       public         postgres    false    309            �           1259    121797    veicoli_segnalazione_1694eff9    INDEX     b   CREATE INDEX veicoli_segnalazione_1694eff9 ON veicoli_segnalazione USING btree (manutenzione_id);
 1   DROP INDEX public.veicoli_segnalazione_1694eff9;
       public         postgres    false    311            �           1259    121798    veicoli_segnalazione_36063dc9    INDEX     \   CREATE INDEX veicoli_segnalazione_36063dc9 ON veicoli_segnalazione USING btree (creazione);
 1   DROP INDEX public.veicoli_segnalazione_36063dc9;
       public         postgres    false    311            �           1259    121799    veicoli_segnalazione_69bd2e5f    INDEX     b   CREATE INDEX veicoli_segnalazione_69bd2e5f ON veicoli_segnalazione USING btree (ultima_modifica);
 1   DROP INDEX public.veicoli_segnalazione_69bd2e5f;
       public         postgres    false    311            �           1259    121800    veicoli_segnalazione_9431c155    INDEX     ]   CREATE INDEX veicoli_segnalazione_9431c155 ON veicoli_segnalazione USING btree (veicolo_id);
 1   DROP INDEX public.veicoli_segnalazione_9431c155;
       public         postgres    false    311            �           1259    121801    veicoli_segnalazione_fa6f1f24    INDEX     \   CREATE INDEX veicoli_segnalazione_fa6f1f24 ON veicoli_segnalazione USING btree (autore_id);
 1   DROP INDEX public.veicoli_segnalazione_fa6f1f24;
       public         postgres    false    311            �           1259    121802    veicoli_veicolo_0844b6f9    INDEX     N   CREATE INDEX veicoli_veicolo_0844b6f9 ON veicoli_veicolo USING btree (targa);
 ,   DROP INDEX public.veicoli_veicolo_0844b6f9;
       public         postgres    false    313            �           1259    121803    veicoli_veicolo_256d016a    INDEX     R   CREATE INDEX veicoli_veicolo_256d016a ON veicoli_veicolo USING btree (categoria);
 ,   DROP INDEX public.veicoli_veicolo_256d016a;
       public         postgres    false    313            �           1259    121804    veicoli_veicolo_351fd66c    INDEX     Q   CREATE INDEX veicoli_veicolo_351fd66c ON veicoli_veicolo USING btree (libretto);
 ,   DROP INDEX public.veicoli_veicolo_351fd66c;
       public         postgres    false    313            �           1259    121805    veicoli_veicolo_36063dc9    INDEX     R   CREATE INDEX veicoli_veicolo_36063dc9 ON veicoli_veicolo USING btree (creazione);
 ,   DROP INDEX public.veicoli_veicolo_36063dc9;
       public         postgres    false    313            �           1259    121806    veicoli_veicolo_3c04da3f    INDEX     ^   CREATE INDEX veicoli_veicolo_3c04da3f ON veicoli_veicolo USING btree (data_immatricolazione);
 ,   DROP INDEX public.veicoli_veicolo_3c04da3f;
       public         postgres    false    313            �           1259    121807    veicoli_veicolo_558318fe    INDEX     _   CREATE INDEX veicoli_veicolo_558318fe ON veicoli_veicolo USING btree (prima_immatricolazione);
 ,   DROP INDEX public.veicoli_veicolo_558318fe;
       public         postgres    false    313            �           1259    121808    veicoli_veicolo_69bd2e5f    INDEX     X   CREATE INDEX veicoli_veicolo_69bd2e5f ON veicoli_veicolo USING btree (ultima_modifica);
 ,   DROP INDEX public.veicoli_veicolo_69bd2e5f;
       public         postgres    false    313            �           1259    121809 '   veicoli_veicolo_categoria_ae91837d_like    INDEX     u   CREATE INDEX veicoli_veicolo_categoria_ae91837d_like ON veicoli_veicolo USING btree (categoria varchar_pattern_ops);
 ;   DROP INDEX public.veicoli_veicolo_categoria_ae91837d_like;
       public         postgres    false    313            �           1259    121810 &   veicoli_veicolo_libretto_131fa9ab_like    INDEX     s   CREATE INDEX veicoli_veicolo_libretto_131fa9ab_like ON veicoli_veicolo USING btree (libretto varchar_pattern_ops);
 :   DROP INDEX public.veicoli_veicolo_libretto_131fa9ab_like;
       public         postgres    false    313            �           1259    121811 #   veicoli_veicolo_targa_4f13d1eb_like    INDEX     m   CREATE INDEX veicoli_veicolo_targa_4f13d1eb_like ON veicoli_veicolo USING btree (targa varchar_pattern_ops);
 7   DROP INDEX public.veicoli_veicolo_targa_4f13d1eb_like;
       public         postgres    false    313            �           1259    121812 $   veicoli_veicolo_telaio_f2649410_like    INDEX     o   CREATE INDEX veicoli_veicolo_telaio_f2649410_like ON veicoli_veicolo USING btree (telaio varchar_pattern_ops);
 8   DROP INDEX public.veicoli_veicolo_telaio_f2649410_like;
       public         postgres    false    313            �           2606    121813     D03c7b0530f486d7c5931579030f6ccd    FK CONSTRAINT     �   ALTER TABLE ONLY base_autorizzazione
    ADD CONSTRAINT "D03c7b0530f486d7c5931579030f6ccd" FOREIGN KEY (destinatario_oggetto_tipo_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 `   ALTER TABLE ONLY public.base_autorizzazione DROP CONSTRAINT "D03c7b0530f486d7c5931579030f6ccd";
       public       postgres    false    251    233    3991            �           2606    121818 ?   anagrafi_appartenenza_id_04e6f381_fk_anagrafica_appartenenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_riserva
    ADD CONSTRAINT anagrafi_appartenenza_id_04e6f381_fk_anagrafica_appartenenza_id FOREIGN KEY (appartenenza_id) REFERENCES anagrafica_appartenenza(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.anagrafica_riserva DROP CONSTRAINT anagrafi_appartenenza_id_04e6f381_fk_anagrafica_appartenenza_id;
       public       postgres    false    187    203    3636            �           2606    121823 ?   anagrafi_appartenenza_id_bbf1065a_fk_anagrafica_appartenenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_dimissione
    ADD CONSTRAINT anagrafi_appartenenza_id_bbf1065a_fk_anagrafica_appartenenza_id FOREIGN KEY (appartenenza_id) REFERENCES anagrafica_appartenenza(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_dimissione DROP CONSTRAINT anagrafi_appartenenza_id_bbf1065a_fk_anagrafica_appartenenza_id;
       public       postgres    false    3636    191    187            �           2606    121828 ?   anagrafi_appartenenza_id_d2133a52_fk_anagrafica_appartenenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_estensione
    ADD CONSTRAINT anagrafi_appartenenza_id_d2133a52_fk_anagrafica_appartenenza_id FOREIGN KEY (appartenenza_id) REFERENCES anagrafica_appartenenza(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_estensione DROP CONSTRAINT anagrafi_appartenenza_id_d2133a52_fk_anagrafica_appartenenza_id;
       public       postgres    false    3636    195    187            �           2606    121833 ?   anagrafi_appartenenza_id_fac52e73_fk_anagrafica_appartenenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_trasferimento
    ADD CONSTRAINT anagrafi_appartenenza_id_fac52e73_fk_anagrafica_appartenenza_id FOREIGN KEY (appartenenza_id) REFERENCES anagrafica_appartenenza(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_trasferimento DROP CONSTRAINT anagrafi_appartenenza_id_fac52e73_fk_anagrafica_appartenenza_id;
       public       postgres    false    209    187    3636            �           2606    121838 ?   anagrafica_appar_vecchia_sede_id_02e00b6e_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_appartenenza
    ADD CONSTRAINT anagrafica_appar_vecchia_sede_id_02e00b6e_fk_anagrafica_sede_id FOREIGN KEY (vecchia_sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_appartenenza DROP CONSTRAINT anagrafica_appar_vecchia_sede_id_02e00b6e_fk_anagrafica_sede_id;
       public       postgres    false    3766    205    187            �           2606    121843 ?   anagrafica_apparte_persona_id_064511d5_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_appartenenza
    ADD CONSTRAINT anagrafica_apparte_persona_id_064511d5_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_appartenenza DROP CONSTRAINT anagrafica_apparte_persona_id_064511d5_fk_anagrafica_persona_id;
       public       postgres    false    187    199    3718            �           2606    121848 >   anagrafica_appartenenza_sede_id_08aaa687_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_appartenenza
    ADD CONSTRAINT anagrafica_appartenenza_sede_id_08aaa687_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_appartenenza DROP CONSTRAINT anagrafica_appartenenza_sede_id_08aaa687_fk_anagrafica_sede_id;
       public       postgres    false    187    205    3766            �           2606    121853 ?   anagrafica_d_oggetto_tipo_id_525c06dc_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_delega
    ADD CONSTRAINT anagrafica_d_oggetto_tipo_id_525c06dc_fk_django_content_type_id FOREIGN KEY (oggetto_tipo_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.anagrafica_delega DROP CONSTRAINT anagrafica_d_oggetto_tipo_id_525c06dc_fk_django_content_type_id;
       public       postgres    false    3991    251    189            �           2606    121858 ?   anagrafica_dele_firmatario_id_8c5c80ff_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_delega
    ADD CONSTRAINT anagrafica_dele_firmatario_id_8c5c80ff_fk_anagrafica_persona_id FOREIGN KEY (firmatario_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.anagrafica_delega DROP CONSTRAINT anagrafica_dele_firmatario_id_8c5c80ff_fk_anagrafica_persona_id;
       public       postgres    false    189    3718    199            �           2606    121863 >   anagrafica_delega_persona_id_41d95896_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_delega
    ADD CONSTRAINT anagrafica_delega_persona_id_41d95896_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.anagrafica_delega DROP CONSTRAINT anagrafica_delega_persona_id_41d95896_fk_anagrafica_persona_id;
       public       postgres    false    199    189    3718            �           2606    121868 ?   anagrafica_dim_richiedente_id_279215a5_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_dimissione
    ADD CONSTRAINT anagrafica_dim_richiedente_id_279215a5_fk_anagrafica_persona_id FOREIGN KEY (richiedente_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_dimissione DROP CONSTRAINT anagrafica_dim_richiedente_id_279215a5_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    191            �           2606    121873 ?   anagrafica_dimissi_persona_id_85579005_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_dimissione
    ADD CONSTRAINT anagrafica_dimissi_persona_id_85579005_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_dimissione DROP CONSTRAINT anagrafica_dimissi_persona_id_85579005_fk_anagrafica_persona_id;
       public       postgres    false    3718    191    199            �           2606    121878 <   anagrafica_dimissione_sede_id_676796e1_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_dimissione
    ADD CONSTRAINT anagrafica_dimissione_sede_id_676796e1_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.anagrafica_dimissione DROP CONSTRAINT anagrafica_dimissione_sede_id_676796e1_fk_anagrafica_sede_id;
       public       postgres    false    191    3766    205            �           2606    121883 ?   anagrafica_documen_persona_id_60d1ad0a_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_documento
    ADD CONSTRAINT anagrafica_documen_persona_id_60d1ad0a_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.anagrafica_documento DROP CONSTRAINT anagrafica_documen_persona_id_60d1ad0a_fk_anagrafica_persona_id;
       public       postgres    false    199    193    3718            �           2606    121888 ?   anagrafica_est_richiedente_id_65472ff0_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_estensione
    ADD CONSTRAINT anagrafica_est_richiedente_id_65472ff0_fk_anagrafica_persona_id FOREIGN KEY (richiedente_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_estensione DROP CONSTRAINT anagrafica_est_richiedente_id_65472ff0_fk_anagrafica_persona_id;
       public       postgres    false    195    3718    199            �           2606    121893 ?   anagrafica_esten_destinazione_id_72b0edee_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_estensione
    ADD CONSTRAINT anagrafica_esten_destinazione_id_72b0edee_fk_anagrafica_sede_id FOREIGN KEY (destinazione_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_estensione DROP CONSTRAINT anagrafica_esten_destinazione_id_72b0edee_fk_anagrafica_sede_id;
       public       postgres    false    3766    205    195            �           2606    121898 ?   anagrafica_estensi_persona_id_5d104815_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_estensione
    ADD CONSTRAINT anagrafica_estensi_persona_id_5d104815_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.anagrafica_estensione DROP CONSTRAINT anagrafica_estensi_persona_id_5d104815_fk_anagrafica_persona_id;
       public       postgres    false    199    195    3718            �           2606    121903 ?   anagrafica_fototes_persona_id_5dac709a_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_fototessera
    ADD CONSTRAINT anagrafica_fototes_persona_id_5dac709a_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_fototessera DROP CONSTRAINT anagrafica_fototes_persona_id_5dac709a_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    197            �           2606    121908 ?   anagrafica_p_registrato_da_id_144bab34_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_provvedimentodisciplinare
    ADD CONSTRAINT anagrafica_p_registrato_da_id_144bab34_fk_anagrafica_persona_id FOREIGN KEY (registrato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_provvedimentodisciplinare DROP CONSTRAINT anagrafica_p_registrato_da_id_144bab34_fk_anagrafica_persona_id;
       public       postgres    false    201    3718    199            �           2606    121913 ?   anagrafica_precedente_id_f35c0bad_fk_anagrafica_appartenenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_appartenenza
    ADD CONSTRAINT anagrafica_precedente_id_f35c0bad_fk_anagrafica_appartenenza_id FOREIGN KEY (precedente_id) REFERENCES anagrafica_appartenenza(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_appartenenza DROP CONSTRAINT anagrafica_precedente_id_f35c0bad_fk_anagrafica_appartenenza_id;
       public       postgres    false    187    187    3636            �           2606    121918 ?   anagrafica_provved_persona_id_d9bd7c7c_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_provvedimentodisciplinare
    ADD CONSTRAINT anagrafica_provved_persona_id_d9bd7c7c_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_provvedimentodisciplinare DROP CONSTRAINT anagrafica_provved_persona_id_d9bd7c7c_fk_anagrafica_persona_id;
       public       postgres    false    3718    201    199            �           2606    121923 ?   anagrafica_provvedimento_sede_id_f1f5226e_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_provvedimentodisciplinare
    ADD CONSTRAINT anagrafica_provvedimento_sede_id_f1f5226e_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_provvedimentodisciplinare DROP CONSTRAINT anagrafica_provvedimento_sede_id_f1f5226e_fk_anagrafica_sede_id;
       public       postgres    false    205    3766    201            �           2606    121928 ?   anagrafica_riserva_persona_id_292e673a_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_riserva
    ADD CONSTRAINT anagrafica_riserva_persona_id_292e673a_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.anagrafica_riserva DROP CONSTRAINT anagrafica_riserva_persona_id_292e673a_fk_anagrafica_persona_id;
       public       postgres    false    199    203    3718            �           2606    121933 :   anagrafica_sede_genitore_id_abc0e096_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_sede
    ADD CONSTRAINT anagrafica_sede_genitore_id_abc0e096_fk_anagrafica_sede_id FOREIGN KEY (genitore_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.anagrafica_sede DROP CONSTRAINT anagrafica_sede_genitore_id_abc0e096_fk_anagrafica_sede_id;
       public       postgres    false    3766    205    205            �           2606    121938 :   anagrafica_sede_locazione_id_65857ef3_fk_base_locazione_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_sede
    ADD CONSTRAINT anagrafica_sede_locazione_id_65857ef3_fk_base_locazione_id FOREIGN KEY (locazione_id) REFERENCES base_locazione(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.anagrafica_sede DROP CONSTRAINT anagrafica_sede_locazione_id_65857ef3_fk_base_locazione_id;
       public       postgres    false    3925    235    205            �           2606    121943 ?   anagrafica_telefon_persona_id_ffadc83e_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_telefono
    ADD CONSTRAINT anagrafica_telefon_persona_id_ffadc83e_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.anagrafica_telefono DROP CONSTRAINT anagrafica_telefon_persona_id_ffadc83e_fk_anagrafica_persona_id;
       public       postgres    false    207    199    3718            �           2606    121948 ?   anagrafica_tra_richiedente_id_fbd9320a_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_trasferimento
    ADD CONSTRAINT anagrafica_tra_richiedente_id_fbd9320a_fk_anagrafica_persona_id FOREIGN KEY (richiedente_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_trasferimento DROP CONSTRAINT anagrafica_tra_richiedente_id_fbd9320a_fk_anagrafica_persona_id;
       public       postgres    false    3718    209    199            �           2606    121953 ?   anagrafica_trasf_destinazione_id_1ca99bfb_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_trasferimento
    ADD CONSTRAINT anagrafica_trasf_destinazione_id_1ca99bfb_fk_anagrafica_sede_id FOREIGN KEY (destinazione_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_trasferimento DROP CONSTRAINT anagrafica_trasf_destinazione_id_1ca99bfb_fk_anagrafica_sede_id;
       public       postgres    false    209    205    3766            �           2606    121958 ?   anagrafica_trasfer_persona_id_aa5a579b_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY anagrafica_trasferimento
    ADD CONSTRAINT anagrafica_trasfer_persona_id_aa5a579b_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.anagrafica_trasferimento DROP CONSTRAINT anagrafica_trasfer_persona_id_aa5a579b_fk_anagrafica_persona_id;
       public       postgres    false    199    209    3718            �           2606    121963 4   attivita_area_sede_id_a49ce0f1_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_area
    ADD CONSTRAINT attivita_area_sede_id_a49ce0f1_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.attivita_area DROP CONSTRAINT attivita_area_sede_id_a49ce0f1_fk_anagrafica_sede_id;
       public       postgres    false    205    211    3766            �           2606    121968 6   attivita_attivita_area_id_a11c4a8d_fk_attivita_area_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_attivita
    ADD CONSTRAINT attivita_attivita_area_id_a11c4a8d_fk_attivita_area_id FOREIGN KEY (area_id) REFERENCES attivita_area(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.attivita_attivita DROP CONSTRAINT attivita_attivita_area_id_a11c4a8d_fk_attivita_area_id;
       public       postgres    false    3792    213    211            �           2606    121973 >   attivita_attivita_estensione_id_5e2a5b13_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_attivita
    ADD CONSTRAINT attivita_attivita_estensione_id_5e2a5b13_fk_anagrafica_sede_id FOREIGN KEY (estensione_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.attivita_attivita DROP CONSTRAINT attivita_attivita_estensione_id_5e2a5b13_fk_anagrafica_sede_id;
       public       postgres    false    3766    213    205            �           2606    121978 <   attivita_attivita_locazione_id_4639636b_fk_base_locazione_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_attivita
    ADD CONSTRAINT attivita_attivita_locazione_id_4639636b_fk_base_locazione_id FOREIGN KEY (locazione_id) REFERENCES base_locazione(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.attivita_attivita DROP CONSTRAINT attivita_attivita_locazione_id_4639636b_fk_base_locazione_id;
       public       postgres    false    213    3925    235            �           2606    121983 8   attivita_attivita_sede_id_462d8d23_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_attivita
    ADD CONSTRAINT attivita_attivita_sede_id_462d8d23_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.attivita_attivita DROP CONSTRAINT attivita_attivita_sede_id_462d8d23_fk_anagrafica_sede_id;
       public       postgres    false    213    205    3766            �           2606    121988 ?   attivita_partecipa_persona_id_903e460a_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_partecipazione
    ADD CONSTRAINT attivita_partecipa_persona_id_903e460a_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.attivita_partecipazione DROP CONSTRAINT attivita_partecipa_persona_id_903e460a_fk_anagrafica_persona_id;
       public       postgres    false    215    3718    199            �           2606    121993 >   attivita_partecipazione_turno_id_345a6a4c_fk_attivita_turno_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_partecipazione
    ADD CONSTRAINT attivita_partecipazione_turno_id_345a6a4c_fk_attivita_turno_id FOREIGN KEY (turno_id) REFERENCES attivita_turno(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.attivita_partecipazione DROP CONSTRAINT attivita_partecipazione_turno_id_345a6a4c_fk_attivita_turno_id;
       public       postgres    false    217    3845    215            �           2606    121998 ;   attivita_turno_attivita_id_4ac33164_fk_attivita_attivita_id    FK CONSTRAINT     �   ALTER TABLE ONLY attivita_turno
    ADD CONSTRAINT attivita_turno_attivita_id_4ac33164_fk_attivita_attivita_id FOREIGN KEY (attivita_id) REFERENCES attivita_attivita(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.attivita_turno DROP CONSTRAINT attivita_turno_attivita_id_4ac33164_fk_attivita_attivita_id;
       public       postgres    false    3810    217    213            �           2606    122003 ?   autenticazione_u_utenza_id_1f5e16e3_fk_autenticazione_utenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_user_permissions
    ADD CONSTRAINT autenticazione_u_utenza_id_1f5e16e3_fk_autenticazione_utenza_id FOREIGN KEY (utenza_id) REFERENCES autenticazione_utenza(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.autenticazione_utenza_user_permissions DROP CONSTRAINT autenticazione_u_utenza_id_1f5e16e3_fk_autenticazione_utenza_id;
       public       postgres    false    3854    223    219            �           2606    122008 ?   autenticazione_u_utenza_id_5278b250_fk_autenticazione_utenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_groups
    ADD CONSTRAINT autenticazione_u_utenza_id_5278b250_fk_autenticazione_utenza_id FOREIGN KEY (utenza_id) REFERENCES autenticazione_utenza(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.autenticazione_utenza_groups DROP CONSTRAINT autenticazione_u_utenza_id_5278b250_fk_autenticazione_utenza_id;
       public       postgres    false    220    3854    219            �           2606    122013 ?   autenticazione_ute_permission_id_7c96147d_fk_auth_permission_id    FK CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_user_permissions
    ADD CONSTRAINT autenticazione_ute_permission_id_7c96147d_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.autenticazione_utenza_user_permissions DROP CONSTRAINT autenticazione_ute_permission_id_7c96147d_fk_auth_permission_id;
       public       postgres    false    3882    223    229            �           2606    122018 ?   autenticazione_ute_persona_id_b4c4ae3f_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza
    ADD CONSTRAINT autenticazione_ute_persona_id_b4c4ae3f_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.autenticazione_utenza DROP CONSTRAINT autenticazione_ute_persona_id_b4c4ae3f_fk_anagrafica_persona_id;
       public       postgres    false    199    219    3718            �           2606    122023 ?   autenticazione_utenza_groups_group_id_8a1692dc_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY autenticazione_utenza_groups
    ADD CONSTRAINT autenticazione_utenza_groups_group_id_8a1692dc_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.autenticazione_utenza_groups DROP CONSTRAINT autenticazione_utenza_groups_group_id_8a1692dc_fk_auth_group_id;
       public       postgres    false    225    220    3871            �           2606    122028 ?   auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id    FK CONSTRAINT     �   ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id;
       public       postgres    false    227    3882    229            �           2606    122033 9   auth_group_permissions_group_id_b120cbf9_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
       public       postgres    false    227    225    3871            �           2606    122038 ?   auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id;
       public       postgres    false    251    229    3991            �           2606    122043 ?   base_allegat_oggetto_tipo_id_109eb587_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY base_allegato
    ADD CONSTRAINT base_allegat_oggetto_tipo_id_109eb587_fk_django_content_type_id FOREIGN KEY (oggetto_tipo_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.base_allegato DROP CONSTRAINT base_allegat_oggetto_tipo_id_109eb587_fk_django_content_type_id;
       public       postgres    false    251    231    3991            �           2606    122048 ?   base_autoriz_oggetto_tipo_id_3bfdf02a_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY base_autorizzazione
    ADD CONSTRAINT base_autoriz_oggetto_tipo_id_3bfdf02a_fk_django_content_type_id FOREIGN KEY (oggetto_tipo_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.base_autorizzazione DROP CONSTRAINT base_autoriz_oggetto_tipo_id_3bfdf02a_fk_django_content_type_id;
       public       postgres    false    233    3991    251            �           2606    122053 ?   base_autorizza_richiedente_id_6c655591_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY base_autorizzazione
    ADD CONSTRAINT base_autorizza_richiedente_id_6c655591_fk_anagrafica_persona_id FOREIGN KEY (richiedente_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.base_autorizzazione DROP CONSTRAINT base_autorizza_richiedente_id_6c655591_fk_anagrafica_persona_id;
       public       postgres    false    3718    233    199            �           2606    122058 ?   base_autorizzaz_firmatario_id_fe723741_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY base_autorizzazione
    ADD CONSTRAINT base_autorizzaz_firmatario_id_fe723741_fk_anagrafica_persona_id FOREIGN KEY (firmatario_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.base_autorizzazione DROP CONSTRAINT base_autorizzaz_firmatario_id_fe723741_fk_anagrafica_persona_id;
       public       postgres    false    233    3718    199            �           2606    122063 5   base_log_persona_id_0c624ba4_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY base_log
    ADD CONSTRAINT base_log_persona_id_0c624ba4_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 h   ALTER TABLE ONLY public.base_log DROP CONSTRAINT base_log_persona_id_0c624ba4_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    237            �           2606    122068 7   base_token_persona_id_957fc0b3_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY base_token
    ADD CONSTRAINT base_token_persona_id_957fc0b3_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.base_token DROP CONSTRAINT base_token_persona_id_957fc0b3_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    239            �           2606    122073 ?   centrale_opera_smontato_da_id_b603ce13_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY centrale_operativa_turno
    ADD CONSTRAINT centrale_opera_smontato_da_id_b603ce13_fk_anagrafica_persona_id FOREIGN KEY (smontato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.centrale_operativa_turno DROP CONSTRAINT centrale_opera_smontato_da_id_b603ce13_fk_anagrafica_persona_id;
       public       postgres    false    243    199    3718            �           2606    122078 ?   centrale_operat_montato_da_id_4d1ed35d_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY centrale_operativa_turno
    ADD CONSTRAINT centrale_operat_montato_da_id_4d1ed35d_fk_anagrafica_persona_id FOREIGN KEY (montato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.centrale_operativa_turno DROP CONSTRAINT centrale_operat_montato_da_id_4d1ed35d_fk_anagrafica_persona_id;
       public       postgres    false    3718    243    199            �           2606    122083 ?   centrale_operativa_persona_id_0ac5aa99_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY centrale_operativa_reperibilita
    ADD CONSTRAINT centrale_operativa_persona_id_0ac5aa99_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.centrale_operativa_reperibilita DROP CONSTRAINT centrale_operativa_persona_id_0ac5aa99_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    241            �           2606    122088 ?   centrale_operativa_persona_id_f7807a87_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY centrale_operativa_turno
    ADD CONSTRAINT centrale_operativa_persona_id_f7807a87_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.centrale_operativa_turno DROP CONSTRAINT centrale_operativa_persona_id_f7807a87_fk_anagrafica_persona_id;
       public       postgres    false    243    199    3718            �           2606    122093 ?   centrale_operativa_turno_turno_id_ba156072_fk_attivita_turno_id    FK CONSTRAINT     �   ALTER TABLE ONLY centrale_operativa_turno
    ADD CONSTRAINT centrale_operativa_turno_turno_id_ba156072_fk_attivita_turno_id FOREIGN KEY (turno_id) REFERENCES attivita_turno(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.centrale_operativa_turno DROP CONSTRAINT centrale_operativa_turno_turno_id_ba156072_fk_attivita_turno_id;
       public       postgres    false    217    243    3845            �           2606    122098 ?   curriculum__certificato_da_id_ec5bd165_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY curriculum_titolopersonale
    ADD CONSTRAINT curriculum__certificato_da_id_ec5bd165_fk_anagrafica_persona_id FOREIGN KEY (certificato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.curriculum_titolopersonale DROP CONSTRAINT curriculum__certificato_da_id_ec5bd165_fk_anagrafica_persona_id;
       public       postgres    false    3718    247    199            �           2606    122103 ?   curriculum_titolop_persona_id_b8b0fd80_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY curriculum_titolopersonale
    ADD CONSTRAINT curriculum_titolop_persona_id_b8b0fd80_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.curriculum_titolopersonale DROP CONSTRAINT curriculum_titolop_persona_id_b8b0fd80_fk_anagrafica_persona_id;
       public       postgres    false    199    3718    247            �           2606    122108 ?   curriculum_titoloper_titolo_id_81c03310_fk_curriculum_titolo_id    FK CONSTRAINT     �   ALTER TABLE ONLY curriculum_titolopersonale
    ADD CONSTRAINT curriculum_titoloper_titolo_id_81c03310_fk_curriculum_titolo_id FOREIGN KEY (titolo_id) REFERENCES curriculum_titolo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.curriculum_titolopersonale DROP CONSTRAINT curriculum_titoloper_titolo_id_81c03310_fk_curriculum_titolo_id;
       public       postgres    false    3969    245    247            �           2606    122113 ?   django_admin_content_type_id_c4bce8eb_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_content_type_id_c4bce8eb_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_content_type_id_c4bce8eb_fk_django_content_type_id;
       public       postgres    false    251    249    3991            �           2606    122118 =   django_admin_log_user_id_c564eba6_fk_autenticazione_utenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_autenticazione_utenza_id FOREIGN KEY (user_id) REFERENCES autenticazione_utenza(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_c564eba6_fk_autenticazione_utenza_id;
       public       postgres    false    3854    249    219            �           2606    122123 ?   formazion_lezione_id_7b39bf48_fk_formazione_lezionecorsobase_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_assenzacorsobase
    ADD CONSTRAINT formazion_lezione_id_7b39bf48_fk_formazione_lezionecorsobase_id FOREIGN KEY (lezione_id) REFERENCES formazione_lezionecorsobase(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_assenzacorsobase DROP CONSTRAINT formazion_lezione_id_7b39bf48_fk_formazione_lezionecorsobase_id;
       public       postgres    false    4043    266    262            �           2606    122128 ?   formazione_a_registrata_da_id_c68d3670_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_assenzacorsobase
    ADD CONSTRAINT formazione_a_registrata_da_id_c68d3670_fk_anagrafica_persona_id FOREIGN KEY (registrata_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_assenzacorsobase DROP CONSTRAINT formazione_a_registrata_da_id_c68d3670_fk_anagrafica_persona_id;
       public       postgres    false    262    199    3718            �           2606    122133 ?   formazione_aspiran_persona_id_777d488d_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_aspirante
    ADD CONSTRAINT formazione_aspiran_persona_id_777d488d_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.formazione_aspirante DROP CONSTRAINT formazione_aspiran_persona_id_777d488d_fk_anagrafica_persona_id;
       public       postgres    false    260    3718    199            �           2606    122138 ?   formazione_aspirante_locazione_id_9fbeb61b_fk_base_locazione_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_aspirante
    ADD CONSTRAINT formazione_aspirante_locazione_id_9fbeb61b_fk_base_locazione_id FOREIGN KEY (locazione_id) REFERENCES base_locazione(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.formazione_aspirante DROP CONSTRAINT formazione_aspirante_locazione_id_9fbeb61b_fk_base_locazione_id;
       public       postgres    false    3925    260    235            �           2606    122143 ?   formazione_assenza_persona_id_69cb4e91_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_assenzacorsobase
    ADD CONSTRAINT formazione_assenza_persona_id_69cb4e91_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_assenzacorsobase DROP CONSTRAINT formazione_assenza_persona_id_69cb4e91_fk_anagrafica_persona_id;
       public       postgres    false    199    3718    262            �           2606    122148 ?   formazione_corsobase_locazione_id_2497cb8d_fk_base_locazione_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_corsobase
    ADD CONSTRAINT formazione_corsobase_locazione_id_2497cb8d_fk_base_locazione_id FOREIGN KEY (locazione_id) REFERENCES base_locazione(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.formazione_corsobase DROP CONSTRAINT formazione_corsobase_locazione_id_2497cb8d_fk_base_locazione_id;
       public       postgres    false    235    264    3925            �           2606    122153 ;   formazione_corsobase_sede_id_e343ef3e_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_corsobase
    ADD CONSTRAINT formazione_corsobase_sede_id_e343ef3e_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.formazione_corsobase DROP CONSTRAINT formazione_corsobase_sede_id_e343ef3e_fk_anagrafica_sede_id;
       public       postgres    false    3766    205    264            �           2606    122158 ?   formazione_lezione_corso_id_aea20fa3_fk_formazione_corsobase_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_lezionecorsobase
    ADD CONSTRAINT formazione_lezione_corso_id_aea20fa3_fk_formazione_corsobase_id FOREIGN KEY (corso_id) REFERENCES formazione_corsobase(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_lezionecorsobase DROP CONSTRAINT formazione_lezione_corso_id_aea20fa3_fk_formazione_corsobase_id;
       public       postgres    false    4036    264    266            �           2606    122163 ?   formazione_parte_destinazione_id_08e97af7_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_partecipazionecorsobase
    ADD CONSTRAINT formazione_parte_destinazione_id_08e97af7_fk_anagrafica_sede_id FOREIGN KEY (destinazione_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_partecipazionecorsobase DROP CONSTRAINT formazione_parte_destinazione_id_08e97af7_fk_anagrafica_sede_id;
       public       postgres    false    3766    205    268            �           2606    122168 ?   formazione_parteci_corso_id_74c27279_fk_formazione_corsobase_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_partecipazionecorsobase
    ADD CONSTRAINT formazione_parteci_corso_id_74c27279_fk_formazione_corsobase_id FOREIGN KEY (corso_id) REFERENCES formazione_corsobase(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_partecipazionecorsobase DROP CONSTRAINT formazione_parteci_corso_id_74c27279_fk_formazione_corsobase_id;
       public       postgres    false    268    264    4036            �           2606    122173 ?   formazione_parteci_persona_id_541e6502_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY formazione_partecipazionecorsobase
    ADD CONSTRAINT formazione_parteci_persona_id_541e6502_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.formazione_partecipazionecorsobase DROP CONSTRAINT formazione_parteci_persona_id_541e6502_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    268            �           2606    122178 ?   gruppi_appartene_negato_da_id_803face3_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY gruppi_appartenenza
    ADD CONSTRAINT gruppi_appartene_negato_da_id_803face3_fk_anagrafica_persona_id FOREIGN KEY (negato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.gruppi_appartenenza DROP CONSTRAINT gruppi_appartene_negato_da_id_803face3_fk_anagrafica_persona_id;
       public       postgres    false    199    3718    270            �           2606    122183 ?   gruppi_appartenenz_persona_id_898d6042_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY gruppi_appartenenza
    ADD CONSTRAINT gruppi_appartenenz_persona_id_898d6042_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.gruppi_appartenenza DROP CONSTRAINT gruppi_appartenenz_persona_id_898d6042_fk_anagrafica_persona_id;
       public       postgres    false    199    3718    270            �           2606    122188 :   gruppi_appartenenza_gruppo_id_3aa60b25_fk_gruppi_gruppo_id    FK CONSTRAINT     �   ALTER TABLE ONLY gruppi_appartenenza
    ADD CONSTRAINT gruppi_appartenenza_gruppo_id_3aa60b25_fk_gruppi_gruppo_id FOREIGN KEY (gruppo_id) REFERENCES gruppi_gruppo(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.gruppi_appartenenza DROP CONSTRAINT gruppi_appartenenza_gruppo_id_3aa60b25_fk_gruppi_gruppo_id;
       public       postgres    false    272    4079    270            �           2606    122193 2   gruppi_gruppo_area_id_4ebcf904_fk_attivita_area_id    FK CONSTRAINT     �   ALTER TABLE ONLY gruppi_gruppo
    ADD CONSTRAINT gruppi_gruppo_area_id_4ebcf904_fk_attivita_area_id FOREIGN KEY (area_id) REFERENCES attivita_area(id) DEFERRABLE INITIALLY DEFERRED;
 j   ALTER TABLE ONLY public.gruppi_gruppo DROP CONSTRAINT gruppi_gruppo_area_id_4ebcf904_fk_attivita_area_id;
       public       postgres    false    3792    211    272            �           2606    122198 :   gruppi_gruppo_attivita_id_ad6907c3_fk_attivita_attivita_id    FK CONSTRAINT     �   ALTER TABLE ONLY gruppi_gruppo
    ADD CONSTRAINT gruppi_gruppo_attivita_id_ad6907c3_fk_attivita_attivita_id FOREIGN KEY (attivita_id) REFERENCES attivita_attivita(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.gruppi_gruppo DROP CONSTRAINT gruppi_gruppo_attivita_id_ad6907c3_fk_attivita_attivita_id;
       public       postgres    false    213    272    3810            �           2606    122203 4   gruppi_gruppo_sede_id_47ea3ef7_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY gruppi_gruppo
    ADD CONSTRAINT gruppi_gruppo_sede_id_47ea3ef7_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.gruppi_gruppo DROP CONSTRAINT gruppi_gruppo_sede_id_47ea3ef7_fk_anagrafica_sede_id;
       public       postgres    false    3766    272    205                        2606    122208 >   posta_destinatario_messaggio_id_42be8327_fk_posta_messaggio_id    FK CONSTRAINT     �   ALTER TABLE ONLY posta_destinatario
    ADD CONSTRAINT posta_destinatario_messaggio_id_42be8327_fk_posta_messaggio_id FOREIGN KEY (messaggio_id) REFERENCES posta_messaggio(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.posta_destinatario DROP CONSTRAINT posta_destinatario_messaggio_id_42be8327_fk_posta_messaggio_id;
       public       postgres    false    278    4107    280                       2606    122213 ?   posta_destinatario_persona_id_b9084daa_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY posta_destinatario
    ADD CONSTRAINT posta_destinatario_persona_id_b9084daa_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.posta_destinatario DROP CONSTRAINT posta_destinatario_persona_id_b9084daa_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    278                       2606    122218 =   posta_messaggio_mittente_id_6879a1ee_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY posta_messaggio
    ADD CONSTRAINT posta_messaggio_mittente_id_6879a1ee_fk_anagrafica_persona_id FOREIGN KEY (mittente_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.posta_messaggio DROP CONSTRAINT posta_messaggio_mittente_id_6879a1ee_fk_anagrafica_persona_id;
       public       postgres    false    280    3718    199                       2606    122223 ?   posta_messaggio_rispondi_a_id_3d32e584_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY posta_messaggio
    ADD CONSTRAINT posta_messaggio_rispondi_a_id_3d32e584_fk_anagrafica_persona_id FOREIGN KEY (rispondi_a_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.posta_messaggio DROP CONSTRAINT posta_messaggio_rispondi_a_id_3d32e584_fk_anagrafica_persona_id;
       public       postgres    false    3718    280    199                       2606    122228 <   sangue_donatore_persona_id_a00315ba_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY sangue_donatore
    ADD CONSTRAINT sangue_donatore_persona_id_a00315ba_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.sangue_donatore DROP CONSTRAINT sangue_donatore_persona_id_a00315ba_fk_anagrafica_persona_id;
       public       postgres    false    199    282    3718                       2606    122233 6   sangue_donatore_sede_sit_id_2c3f1209_fk_sangue_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY sangue_donatore
    ADD CONSTRAINT sangue_donatore_sede_sit_id_2c3f1209_fk_sangue_sede_id FOREIGN KEY (sede_sit_id) REFERENCES sangue_sede(id) DEFERRABLE INITIALLY DEFERRED;
 p   ALTER TABLE ONLY public.sangue_donatore DROP CONSTRAINT sangue_donatore_sede_sit_id_2c3f1209_fk_sangue_sede_id;
       public       postgres    false    288    4141    282                       2606    122238 =   sangue_donazione_persona_id_6447a25f_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY sangue_donazione
    ADD CONSTRAINT sangue_donazione_persona_id_6447a25f_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.sangue_donazione DROP CONSTRAINT sangue_donazione_persona_id_6447a25f_fk_anagrafica_persona_id;
       public       postgres    false    284    199    3718                       2606    122243 3   sangue_donazione_sede_id_119898bb_fk_sangue_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY sangue_donazione
    ADD CONSTRAINT sangue_donazione_sede_id_119898bb_fk_sangue_sede_id FOREIGN KEY (sede_id) REFERENCES sangue_sede(id) DEFERRABLE INITIALLY DEFERRED;
 n   ALTER TABLE ONLY public.sangue_donazione DROP CONSTRAINT sangue_donazione_sede_id_119898bb_fk_sangue_sede_id;
       public       postgres    false    288    4141    284                       2606    122248 :   sangue_merito_persona_id_7d0173ef_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY sangue_merito
    ADD CONSTRAINT sangue_merito_persona_id_7d0173ef_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.sangue_merito DROP CONSTRAINT sangue_merito_persona_id_7d0173ef_fk_anagrafica_persona_id;
       public       postgres    false    286    199    3718            	           2606    122253 ?   social_comme_oggetto_tipo_id_31ea5d6b_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY social_commento
    ADD CONSTRAINT social_comme_oggetto_tipo_id_31ea5d6b_fk_django_content_type_id FOREIGN KEY (oggetto_tipo_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.social_commento DROP CONSTRAINT social_comme_oggetto_tipo_id_31ea5d6b_fk_django_content_type_id;
       public       postgres    false    3991    251    290            
           2606    122258 ;   social_commento_autore_id_601127ed_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY social_commento
    ADD CONSTRAINT social_commento_autore_id_601127ed_fk_anagrafica_persona_id FOREIGN KEY (autore_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.social_commento DROP CONSTRAINT social_commento_autore_id_601127ed_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    290                       2606    122263 ?   social_giudi_oggetto_tipo_id_ccf20414_fk_django_content_type_id    FK CONSTRAINT     �   ALTER TABLE ONLY social_giudizio
    ADD CONSTRAINT social_giudi_oggetto_tipo_id_ccf20414_fk_django_content_type_id FOREIGN KEY (oggetto_tipo_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.social_giudizio DROP CONSTRAINT social_giudi_oggetto_tipo_id_ccf20414_fk_django_content_type_id;
       public       postgres    false    3991    292    251                       2606    122268 ;   social_giudizio_autore_id_dc0341db_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY social_giudizio
    ADD CONSTRAINT social_giudizio_autore_id_dc0341db_fk_anagrafica_persona_id FOREIGN KEY (autore_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.social_giudizio DROP CONSTRAINT social_giudizio_autore_id_dc0341db_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    292                       2606    122273 ?   ufficio__appartenenza_id_5e262408_fk_anagrafica_appartenenza_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio__appartenenza_id_5e262408_fk_anagrafica_appartenenza_id FOREIGN KEY (appartenenza_id) REFERENCES anagrafica_appartenenza(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio__appartenenza_id_5e262408_fk_anagrafica_appartenenza_id;
       public       postgres    false    3636    295    187                       2606    122278 ?   ufficio_soc_riconsegnato_a_id_cc867051_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soc_riconsegnato_a_id_cc867051_fk_anagrafica_persona_id FOREIGN KEY (riconsegnato_a_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soc_riconsegnato_a_id_cc867051_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    299                       2606    122283 ?   ufficio_soci__annullato_da_id_aeb6d74c_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio_soci__annullato_da_id_aeb6d74c_fk_anagrafica_persona_id FOREIGN KEY (annullato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio_soci__annullato_da_id_aeb6d74c_fk_anagrafica_persona_id;
       public       postgres    false    295    3718    199                       2606    122288 ?   ufficio_soci__richiesto_da_id_e6ee13c8_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soci__richiesto_da_id_e6ee13c8_fk_anagrafica_persona_id FOREIGN KEY (richiesto_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soci__richiesto_da_id_e6ee13c8_fk_anagrafica_persona_id;
       public       postgres    false    299    3718    199                       2606    122293 ?   ufficio_soci_confermato_da_id_15a2fad3_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soci_confermato_da_id_15a2fad3_fk_anagrafica_persona_id FOREIGN KEY (confermato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soci_confermato_da_id_15a2fad3_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    299                       2606    122298 ?   ufficio_soci_quota_persona_id_1055e386_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio_soci_quota_persona_id_1055e386_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio_soci_quota_persona_id_1055e386_fk_anagrafica_persona_id;
       public       postgres    false    3718    295    199                       2606    122303 9   ufficio_soci_quota_sede_id_29ade660_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio_soci_quota_sede_id_29ade660_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio_soci_quota_sede_id_29ade660_fk_anagrafica_sede_id;
       public       postgres    false    205    295    3766                       2606    122308 ?   ufficio_soci_registrato_da_id_99ea06f3_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_quota
    ADD CONSTRAINT ufficio_soci_registrato_da_id_99ea06f3_fk_anagrafica_persona_id FOREIGN KEY (registrato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.ufficio_soci_quota DROP CONSTRAINT ufficio_soci_registrato_da_id_99ea06f3_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    295                       2606    122313 ?   ufficio_soci_tesse_persona_id_0be95188_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soci_tesse_persona_id_0be95188_fk_anagrafica_persona_id FOREIGN KEY (persona_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soci_tesse_persona_id_0be95188_fk_anagrafica_persona_id;
       public       postgres    false    199    299    3718                       2606    122318 ?   ufficio_soci_tesser_emesso_da_id_6be4cdf3_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY ufficio_soci_tesserino
    ADD CONSTRAINT ufficio_soci_tesser_emesso_da_id_6be4cdf3_fk_anagrafica_sede_id FOREIGN KEY (emesso_da_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.ufficio_soci_tesserino DROP CONSTRAINT ufficio_soci_tesser_emesso_da_id_6be4cdf3_fk_anagrafica_sede_id;
       public       postgres    false    205    3766    299                       2606    122323 <   veicoli_autoparco_locazione_id_04b9637c_fk_base_locazione_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_autoparco
    ADD CONSTRAINT veicoli_autoparco_locazione_id_04b9637c_fk_base_locazione_id FOREIGN KEY (locazione_id) REFERENCES base_locazione(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.veicoli_autoparco DROP CONSTRAINT veicoli_autoparco_locazione_id_04b9637c_fk_base_locazione_id;
       public       postgres    false    3925    301    235                       2606    122328 8   veicoli_autoparco_sede_id_857db6e7_fk_anagrafica_sede_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_autoparco
    ADD CONSTRAINT veicoli_autoparco_sede_id_857db6e7_fk_anagrafica_sede_id FOREIGN KEY (sede_id) REFERENCES anagrafica_sede(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.veicoli_autoparco DROP CONSTRAINT veicoli_autoparco_sede_id_857db6e7_fk_anagrafica_sede_id;
       public       postgres    false    205    3766    301                       2606    122333 ?   veicoli_collocaz_creato_da_id_ae51cb5c_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_collocazione
    ADD CONSTRAINT veicoli_collocaz_creato_da_id_ae51cb5c_fk_anagrafica_persona_id FOREIGN KEY (creato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_collocazione DROP CONSTRAINT veicoli_collocaz_creato_da_id_ae51cb5c_fk_anagrafica_persona_id;
       public       postgres    false    3718    199    303                       2606    122338 ?   veicoli_collocazi_autoparco_id_371a448a_fk_veicoli_autoparco_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_collocazione
    ADD CONSTRAINT veicoli_collocazi_autoparco_id_371a448a_fk_veicoli_autoparco_id FOREIGN KEY (autoparco_id) REFERENCES veicoli_autoparco(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_collocazione DROP CONSTRAINT veicoli_collocazi_autoparco_id_371a448a_fk_veicoli_autoparco_id;
       public       postgres    false    301    4211    303                       2606    122343 >   veicoli_collocazione_veicolo_id_067437cb_fk_veicoli_veicolo_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_collocazione
    ADD CONSTRAINT veicoli_collocazione_veicolo_id_067437cb_fk_veicoli_veicolo_id FOREIGN KEY (veicolo_id) REFERENCES veicoli_veicolo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.veicoli_collocazione DROP CONSTRAINT veicoli_collocazione_veicolo_id_067437cb_fk_veicoli_veicolo_id;
       public       postgres    false    313    4268    303                       2606    122348 ?   veicoli_fermotec_creato_da_id_8498d659_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_fermotecnico
    ADD CONSTRAINT veicoli_fermotec_creato_da_id_8498d659_fk_anagrafica_persona_id FOREIGN KEY (creato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_fermotecnico DROP CONSTRAINT veicoli_fermotec_creato_da_id_8498d659_fk_anagrafica_persona_id;
       public       postgres    false    305    3718    199                       2606    122353 >   veicoli_fermotecnico_veicolo_id_2d46096c_fk_veicoli_veicolo_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_fermotecnico
    ADD CONSTRAINT veicoli_fermotecnico_veicolo_id_2d46096c_fk_veicoli_veicolo_id FOREIGN KEY (veicolo_id) REFERENCES veicoli_veicolo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.veicoli_fermotecnico DROP CONSTRAINT veicoli_fermotecnico_veicolo_id_2d46096c_fk_veicoli_veicolo_id;
       public       postgres    false    313    305    4268                       2606    122358 ?   veicoli_manutenz_creato_da_id_ebaa78d2_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_manutenzione
    ADD CONSTRAINT veicoli_manutenz_creato_da_id_ebaa78d2_fk_anagrafica_persona_id FOREIGN KEY (creato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_manutenzione DROP CONSTRAINT veicoli_manutenz_creato_da_id_ebaa78d2_fk_anagrafica_persona_id;
       public       postgres    false    307    199    3718                       2606    122363 >   veicoli_manutenzione_veicolo_id_1a700888_fk_veicoli_veicolo_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_manutenzione
    ADD CONSTRAINT veicoli_manutenzione_veicolo_id_1a700888_fk_veicoli_veicolo_id FOREIGN KEY (veicolo_id) REFERENCES veicoli_veicolo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.veicoli_manutenzione DROP CONSTRAINT veicoli_manutenzione_veicolo_id_1a700888_fk_veicoli_veicolo_id;
       public       postgres    false    307    4268    313                        2606    122368 ?   veicoli_rifornim_creato_da_id_abf7ab3b_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_rifornimento
    ADD CONSTRAINT veicoli_rifornim_creato_da_id_abf7ab3b_fk_anagrafica_persona_id FOREIGN KEY (creato_da_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_rifornimento DROP CONSTRAINT veicoli_rifornim_creato_da_id_abf7ab3b_fk_anagrafica_persona_id;
       public       postgres    false    309    3718    199            !           2606    122373 >   veicoli_rifornimento_veicolo_id_81607143_fk_veicoli_veicolo_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_rifornimento
    ADD CONSTRAINT veicoli_rifornimento_veicolo_id_81607143_fk_veicoli_veicolo_id FOREIGN KEY (veicolo_id) REFERENCES veicoli_veicolo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.veicoli_rifornimento DROP CONSTRAINT veicoli_rifornimento_veicolo_id_81607143_fk_veicoli_veicolo_id;
       public       postgres    false    309    4268    313            "           2606    122378 ?   veicoli_seg_manutenzione_id_c425b9c1_fk_veicoli_manutenzione_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_segnalazione
    ADD CONSTRAINT veicoli_seg_manutenzione_id_c425b9c1_fk_veicoli_manutenzione_id FOREIGN KEY (manutenzione_id) REFERENCES veicoli_manutenzione(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_segnalazione DROP CONSTRAINT veicoli_seg_manutenzione_id_c425b9c1_fk_veicoli_manutenzione_id;
       public       postgres    false    311    4236    307            #           2606    122383 ?   veicoli_segnalazion_autore_id_942ad54b_fk_anagrafica_persona_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_segnalazione
    ADD CONSTRAINT veicoli_segnalazion_autore_id_942ad54b_fk_anagrafica_persona_id FOREIGN KEY (autore_id) REFERENCES anagrafica_persona(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.veicoli_segnalazione DROP CONSTRAINT veicoli_segnalazion_autore_id_942ad54b_fk_anagrafica_persona_id;
       public       postgres    false    311    199    3718            $           2606    122388 >   veicoli_segnalazione_veicolo_id_8f05da98_fk_veicoli_veicolo_id    FK CONSTRAINT     �   ALTER TABLE ONLY veicoli_segnalazione
    ADD CONSTRAINT veicoli_segnalazione_veicolo_id_8f05da98_fk_veicoli_veicolo_id FOREIGN KEY (veicolo_id) REFERENCES veicoli_veicolo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.veicoli_segnalazione DROP CONSTRAINT veicoli_segnalazione_veicolo_id_8f05da98_fk_veicoli_veicolo_id;
       public       postgres    false    311    313    4268            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   o  x���ݎ�6������Y��e��E��(�\(Y몱EW��>Mߥ/֑8Ù��JD~����sD:)���e��ctv��n���f��P�o�0^o��0R��e{��m��G�X��~��6�a�k�]�ۭq�f�זmǶ d��[�\�i(�Թ�u���
������yz�S�gh&�\��]����z�/���mh"vog��<9*����+AE�5}�9�c�����H?O�$�3
�31������R��OR�H)�+�L�����0iy�]׼����C����J��-a��Jf��-h.�f��]t�C&ˍ���Jzu�PL�� ��ڦi�ݗ����8�xA݉� <�@��$@<�@����>���v���5AOpc'�T��L��mTT]뵹ʬ�_���^���O�PS�˨���ǯK�ئx�"<�P`AJ�LB��\��2����u�W�n�qwu����>��c��n0�@ȟ�xJ��`Hm�'W��<��v��|n�rs�<�dd�-k����Κ.,թ���^�M�M�_ ��0p �xƀ��P��\KP*�6\�c(�3�c�AƠ����Kݹ��D=AϮu�ܛ�\N��WP�ϲH\"�v�HGW���e�{W
��3�uX
`���Ʃ�ײ�����i#kk��k"�B�:���XGo?������Gzcw�c�	�8b�f�8b�iC��
�Y�j���Ԕ�;/��br�S[{v��)��@�Ye����<;
��&�j����������v����~q�'4�<�\�d0��#�ʙ��/�O���m��(�w����X����F{�WkF�Ā�&��v=��rSx��K���:���TU�Z�Qqy�2�ܹ�����1�nUs=7m����Nm	�8���;0�������)�Np�-����8>
���T��V��@+&a��FÛ�o^����7����7�s�! ?V�X1be5�{G�U�@/�� ����,e��ˋbLzx�c(| `+��Kd>��o�1��3C޲�"���
�2�� �/��#��S�G���L��g��" �By(�AH(&�E0��Oc�|_��>f��L��%�b�KJ(�*5N��zu�$���b�$��@�b���p᠂9�q��I�d�͔�`�3��GS���4K_MY��K9c���ý9"�m�A0��"�H��%am�D���s흏;��N[s�ೋ�cՀ�.j$��&����EԴ.zs���)������K�d�p�#]6��1¾A�P���*%�Δ\��v=@�A�=�@IA�f�����k�}{��~�kE� �����)�2�{���j���Ɩm���jή�F#�Y	���R7��I�]���[�Ϯ$8�%yf%՜ߺs�����j'���W����`Ы�p�
Z������hK\��pS���C+7~=W��D��\$����H~ѽ������+��O���HZ����sɓ���c�2�z���Dy�O�����������i���}1Iy;�"B���0&���3l�ã1�g׵aCUe��ޕ^��nJ��h��ag#h�G�,;Щ����I#DA� (�-�B� +�.�jpT��~���..R#��Al���j@���(O�f�oWwL>�iq�.@b�hdyDȊL֔�i���H�}c_v(��!��f;��ue811$κ8�#�X����u���H�܇W0�D�E<�ъ$)ӊ*�-�θ�q��_�AX��^�ۣ=ٓ�lw@�y��G�N��B�U�K����D@(�r��C�.�c�i��<������.���#4$	�������>*���l�@M���@�	l@q��	�@qk��{�$�v�v���?j���6��ǣ-���j�?�!���x�?�3)���Z~� ��>��"4@���#�.3*Q̿�N���X���\������^S��]��t��rq.��┆LA:���Fɗ��6X"�>=��ܼE�����BL ʓ+��Pu���p��_Ó����Hm�O�Y�0�e�[��L!�*̯����ss�Ի�����񇅙B>�P��%�D�%�"��O��d���3����cά �W
�9�f���U)�      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   y  x�mTђ� |��������b��!� �n��/��X�/�IHBǶej��1��q��V2��w�?C���]�&���۞it����bBy�b"��˥`�l!±�fL
�^/�"�L�S\��>�C���Z3��\���>�eF�r��˧e�������6�w"�@y����K�fʩɫ��ԅ��ЦD��fD������z�)$��Wˢ<E��ے
f0���(&ʻ�G�H}��_r�*��C���J��5l=�EIx�HO��k��O3�P��<y_�'��"�1��:7���q�ԧ��B�^P���zYD���;�W�A�v�Y�������m�ᢪH��@^�q ���w���ݜ�>7RT7��T.�[@,w\��?Q�pl���c�X���6�SN:w'�ׄ�'F�/�Q���L��R!NbVn��Q�D0��՜�����#č���e��9a��8v-[0Л�T����N��@�#�D�7�cA�i54 �O���M����<S���(����&����j$��&�)���J�[if�7�^򊞕DS��_��MB�d�}�N�e�!WYwl��"�M{t,}>��q�&A�.��-)Y��\��l#�T?�����s�d��      �      x������ � �      �   �  x���ˎ۸���AV����#@Pl���m9��sy��I�m�bƚM�I�>Qſ��ݾ�������wB��Kw�ӎ�/B~!��W!���H����ʒ�=�m=�G���4綌҂�
(�k��>X����������8v�%>�>7ԧ�r�o�P,�6:��%'�}����N/)x��<(jN	�����XFHaMt�} �qj�[}�^�~*;���nq��]��w��2�-��ae�"�)0���4ǡy����+Q^��l��x���5��������ù�l�q�LT�ӆ������O�,}�E�����o͸��jkl4Q��8=,X	"S�JKN6����(�ڻ^��k/5�G���zl��1�E pz����8�&)}��S:���z��T`؊�G��&gh�E�FL���gs�aSd8bo�Yd�1��+0\es�C���WB����k��v�A���WJ:�Q�T��&Y����a�sq�������������8I��$p0�&###S%њ!�)*ᴥt�*�����z�ʖ^�,3-R~$K^ YPR�+δHj�]J��Q6յL��+_Bap"�cI�L�)���v����^%{���&Q���GQI�1R�c���v��웡C�*�lp^rH�N<~�C7޺K_�S{��"��S���FZ�Δ�������<8H�]}�Fx��(�����RL2,/�]-�)#���2,˜ᑝJ+����L��L%\Gqe��e&]�kF!�(�s�i�M� Q>2 ���2��]3
!����nŠBY	�7J����Q*M`Hc}�PT&])r��	˔�f�<)2����1F��L*�*ө�딡�Z٧��}�L�R�tG��>�uɧ�N���J=v ��~+��v^ƴ�2�ʹD%z1�{�Z�pәD��\�Vi�3�ʹDq59*�C��z#)���j�afH�a<7��E�`�0��� 7u*J�N�D����� Q��܃<2',�����b�K$���Ү*Tj<��'?�a�d�	�A�J*��:�S]��0D� �LQ� ;��Мz��o�>6�)�����"J*E�Z�B���L�o����.6����(��v�pբ3�cϾ���q+P+�21����m�?0��Nû)���p�R:�f���4���9�g�0���0�C}nǱ9���@�y�)���b\���n���V(;�#��֬l�Rb�5�9��ي���h��c�>��E$��a~+E�����4�����W֪Tbu�L�|:�czB�ͅʇ�dRY����(�'4���z�7�0��m�*���c^���ڟ~�p�Ұhͮ��e�TR(�;`w�����~��7"#��h�nT���wԠ��c���F	N]�C�74�лc���l���[s9��~�_��`h�s)�疏�s�W������������g��لN-����{?�7���U��S����Ц�żUXk�s"�Ɯ�(��x��c2F�XB�Z*�r�R"q6c�m�p�?��h�2ƲE@�jUi�r����3���f�a�qi1*2ƪMŖ�UZ�ɧ�2�:���DJL�����z��iO2����6N"���}��ϔJ����`K��R_j�}&�Ş�oMR���+�Z�t�;��{c�rR�T�m�{��8��?7�ߖ����2-:��٫M����HS� !v�~|9p�ܝ��i���a���s��b y�/FF��0?��´�E�0WS="��x�/H��Z v��(�O�<�pX��R��)|��L�^?��I�� �Jk�`����nD���J�r�>���ά6�����ӱ��Ql\a�i�����oc���;v.5Db�q��g�`�F�dDO�Ϗs���t��~�~�u3 0��+��~���(4r��F�i���2��XN 5l���19}C!����w{(:�^�^�Ƥ2�ye���{k���b�Ҧ7�+ȶ���cG¸f�b@c(�����
��YQ��­u%���+�"t1�!~K�	�����0�0v�q��h�l#�8��W�c�4s ����X�0~����� ���>�52V��S�q����B}�〸/�ρ�O�c��h�=Z�W�5�54^b37�s��R[�
z�a������Mbe7'l�):��8N?'�U_X��k_	��T��̶j�+֨+I��愅0Y㇢�}�f�N�M��������)%4W�u�P�*��]��)I���_��966lq��������u冭      �      x������ � �      �      x�3�L�H�-�I�K��Efs��qqq �<	�      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �             x������ � �            x������ � �      �      x������ � �            x������ � �            x������ � �            x������ � �      	      x������ � �            x������ � �            x������ � �            x������ � �            x������ � �            x������ � �            x������ � �            x������ � �     